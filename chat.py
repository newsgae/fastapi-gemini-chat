from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AI Chat Demo</title>
    </head>
    <body>
        <h1>My AI Chat</h1>
        <input id="messageInput" type="text" placeholder="Type your message here" />
        <button onclick="sendMessage()">Send</button>

        <h2>Reply:</h2>
        <div id="replyBox"></div>

        <script>
            async function sendMessage() {
                const message = document.getElementById("messageInput").value;

                const response = await fetch("/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                document.getElementById("replyBox").innerText = data.reply;
            }
        </script>
    </body>
    </html>
    """


@app.post("/chat")
def chat(request: ChatRequest):
    user_message = request.message
    return {"reply": f"You said: {user_message}"}

# in terminal: python -m uvicorn chat:app
# run http://127.0.0.1:8000

@app.post("/chat2")
def chat2(request: ChatRequest):
    user_message = request.message.lower()

    if "hello" in user_message:
        reply = "Hello! How can I help you?"
    elif "rag" in user_message:
        reply = "RAG means Retrieval Augmented Generation."
    elif "fastapi" in user_message:
        reply = "FastAPI is a modern Python web framework."
    else:
        reply = "I'm a simple AI. Try asking about RAG or FastAPI."

    return {"reply": reply}

# run http://127.0.0.1:8000/docs


@app.get("/chat2", response_class=HTMLResponse)
def chat2_page():
    return """
    <h1>Chat2 AI</h1>
    <input id="msg" />
    <button onclick="send()">Send</button>
    <div id="reply"></div>

    <script>
    async function send() {
        const msg = document.getElementById("msg").value

        const res = await fetch("/chat2", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({message: msg})
        })

        const data = await res.json()
        document.getElementById("reply").innerText = data.reply
    }
    </script>
    """

# run: http://127.0.0.1:8000/chat2