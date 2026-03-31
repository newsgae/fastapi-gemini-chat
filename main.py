from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def hello():
    return {"message": "Hello FastAPI"}

# run http://127.0.0.1:8000/

@app.get("/hello")
def say_hello(name: str):
    return {"message": f"Hello {name}"}

# run http://127.0.0.1:8000/hello?name=Tom
from fastapi.responses import HTMLResponse

@app.get("/web", response_class=HTMLResponse)
def web():
    return """
    <h1>Hello FastAPI</h1>
    """
# run http://127.0.0.1:8000/web