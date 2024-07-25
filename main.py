import uvicorn

import config
import os

from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
app = FastAPI()

# get, post, put, delete

class Body(BaseModel):
    text: str

@app.get("/")
def welcome():
    return {"Hello": "World"}

@app.post("/response")
def generate(body: Body):
    prompt = body.text # User Prompt

    # Upload the user provided file to OpenAI
    message_file = client.files.create(
        file=open("Venkat_Profile.pdf", "rb"), purpose="assistants"
    )

    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
                # Attach the new file to the message.
                "attachments": [
                    {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
                ],
            }
        ]
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=config.assistant_id,
        instructions="Please address the user as Client. The user has a premium account."
    )

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        text = ""
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            latest_message = messages.data[0]
            text = latest_message.content[0].text.value
            print(text)
            break;

    return text

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)



