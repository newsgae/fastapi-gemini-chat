import os

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

client = genai.Client(api_key=API_KEY) if API_KEY else None

# very simple in-memory chat history
# later to replace this with a database or per-user session
chat_history = []

class ChatRequest(BaseModel):
    message: str


@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8" />
        <title>Gemini Multi-turn Chat</title>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 30px auto;
                padding: 0 16px;
            }
            h1 {
                margin-bottom: 20px;
            }
            #chatbox {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 16px;
                min-height: 350px;
                max-height: 550px;
                overflow-y: auto;
                background: #fafafa;
            }
            .msg {
                margin: 12px 0;
                padding: 10px 12px;
                border-radius: 8px;
            }
            .user {
                background: #e8f0fe;
            }
            .assistant {
                background: #f1f3f4;
            }
            .role {
                font-weight: bold;
                margin-bottom: 6px;
            }
            .input-row {
                display: flex;
                gap: 10px;
                margin-top: 16px;
            }
            #msg {
                flex: 1;
                padding: 10px;
                font-size: 16px;
            }
            button {
                padding: 10px 16px;
                font-size: 16px;
                cursor: pointer;
            }
            #status {
                color: #666;
                margin-top: 8px;
                min-height: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Gemini Multi-turn Chat</h1>

        <div id="chatbox"></div>

        <div class="input-row">
            <input id="msg" type="text" placeholder="Type your message here" />
            <button onclick="sendMessage()">Send</button>
            <button onclick="clearHistory()">Clear</button>
        </div>

        <div id="status"></div>

        <script>
            async function loadHistory() {
                const res = await fetch("/history");
                const data = await res.json();
                renderHistory(data.history);
            }

            function renderHistory(history) {
                const chatbox = document.getElementById("chatbox");
                chatbox.innerHTML = "";

                for (const item of history) {
                    const div = document.createElement("div");
                    div.className = "msg " + item.role;

                    const role = document.createElement("div");
                    role.className = "role";
                    role.innerText = item.role === "user" ? "You" : "AI";

                    const content = document.createElement("div");
                    content.innerHTML = marked.parse(item.content || "");

                    div.appendChild(role);
                    div.appendChild(content);
                    chatbox.appendChild(div);
                }

                chatbox.scrollTop = chatbox.scrollHeight;
            }

            async function sendMessage() {
                const input = document.getElementById("msg");
                const status = document.getElementById("status");
                const message = input.value.trim();

                if (!message) return;

                status.innerText = "Thinking...";

                const res = await fetch("/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ message: message })
                });

                const data = await res.json();
                renderHistory(data.history);
                input.value = "";
                status.innerText = "";
            }

            async function clearHistory() {
                const status = document.getElementById("status");
                status.innerText = "Clearing...";

                const res = await fetch("/clear", {
                    method: "POST"
                });

                const data = await res.json();
                renderHistory(data.history);
                status.innerText = "";
            }

            document.getElementById("msg").addEventListener("keydown", function(event) {
                if (event.key === "Enter") {
                    sendMessage();
                }
            });

            loadHistory();
        </script>
    </body>
    </html>
    """


@app.get("/history")
def get_history():
    return {"history": chat_history}


@app.post("/clear")
def clear_history():
    chat_history.clear()
    return {"history": chat_history}


@app.post("/chat")
def chat(request: ChatRequest):
    if not API_KEY:
        return {
            "history": chat_history + [
                {"role": "assistant", "content": "Error: GEMINI_API_KEY not found."}
            ]
        }

    if client is None:
        return {
            "history": chat_history + [
                {"role": "assistant", "content": "Error: Gemini client initialization failed."}
            ]
        }

    user_message = request.message.strip()
    if not user_message:
        return {"history": chat_history}

    chat_history.append({"role": "user", "content": user_message})

    try:
        # Build a text prompt from chat history
        prompt_parts = []
        for item in chat_history:
            if item["role"] == "user":
                prompt_parts.append(f"User: {item['content']}")
            else:
                prompt_parts.append(f"Assistant: {item['content']}")

        prompt_parts.append("Assistant:")
        full_prompt = "\\n".join(prompt_parts)

        response = client.models.generate_content(
            model=MODEL,
            contents=full_prompt,
        )

        reply = response.text or "No response returned."
        chat_history.append({"role": "assistant", "content": reply})

        return {"history": chat_history}

    except Exception as e:
        error_message = f"Error: {str(e)}"
        chat_history.append({"role": "assistant", "content": error_message})
        return {"history": chat_history}

# run in terminal
# cmd: set GEMINI_API_KEY=set YOUR API KEY_api_key
# powershell： $env:GEMINI_API_KEY=”YOUR API KEY“
# python -m uvicorn chat_llm:app --reload
# http://127.0.0.1:8000/chat