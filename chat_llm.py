import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from google import genai
from dotenv import load_dotenv

# load .env
load_dotenv()

# read env variables
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.get("/chat2", response_class=HTMLResponse)
def chat2_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Gemini Chat</title>
    </head>
    <body>
        <h1>Gemini Chat</h1>

        <input id="msg" style="width:300px;" placeholder="Type your message" />
        <button onclick="send()">Send</button>

        <div style="margin-top:20px;">
            <strong>Reply:</strong>
            <div id="reply"></div>
        </div>

        <script>
        async function send() {
            const msg = document.getElementById("msg").value;

            const res = await fetch("/chat2", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: msg })
            });

            const data = await res.json();
            document.getElementById("reply").innerText = data.reply;
        }
        </script>
    </body>
    </html>
    """


@app.post("/chat2")
def chat2(request: ChatRequest):

    if not API_KEY:
        return {"reply": "Error: GEMINI_API_KEY not found"}

    try:
        client = genai.Client(api_key=API_KEY)

        response = client.models.generate_content(
            model=MODEL,
            contents=request.message,
        )

        return {"reply": response.text}

    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

# run in terminal
# cmd: set GEMINI_API_KEY=set AIzaSyB4CfskqhOSXl5xc08G6IefJ0GA3o9IXqM_api_key
# powershell： $env:GEMINI_API_KEY=”AIzaSyB4CfskqhOSXl5xc08G6IefJ0GA3o9IXqM“
# python -m uvicorn chat_llm:app --reload
# http://127.0.0.1:8000/chat2