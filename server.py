from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import base64

app = FastAPI()

# Allow your frontend (knowledge.html, luna.html) to call this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⭐ PASTE YOUR REAL SECRET KEY HERE ⭐
AI_KEY = "YOUR_NEW_SECRET_KEY"

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-4o-mini"


def ask_ai(messages):
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": messages
    }
    r = requests.post(OPENAI_URL, json=body, headers=headers)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


class TextRequest(BaseModel):
    mode: str
    content: str


@app.post("/solve-text")
async def solve_text(req: TextRequest):
    mode = req.mode
    content = req.content

    # ⭐ LUNA CHAT MODE ⭐
    if mode == "chat":
        prompt = f"""
You are Luna, an advanced AI assistant.
You always answer correctly, clearly, and helpfully.
You are warm, intuitive, expressive, and smart.
You explain things simply and beautifully.
You never say you cannot help.
You always give the best possible answer.
User says: {content}
"""
    elif mode == "math":
        prompt = f"You are a math tutor. Solve this step by step:\n\n{content}"
    elif mode == "quiz":
        prompt = f"""
Create 5 quiz questions about: {content}.
Return ONLY JSON:
[
  {{ "type": "mc", "question": "...", "options": ["A","B","C","D"], "correct": "A" }},
  {{ "type": "tf", "question": "...", "correct": "true" }},
  {{ "type": "match", "question": "...", "pairs": [["A","1"],["B","2"]] }}
]
"""
    elif mode == "flashcards":
        prompt = f"""
Create 10 flashcards about: {content}.
Return ONLY JSON:
[
  {{ "front": "Term", "back": "Definition" }}
]
"""
    elif mode == "textbook":
        prompt = f"Explain this text like a teacher:\n\n{content}"
    elif mode == "language":
        prompt = f"Detect the language and explain this simply:\n\n{content}"
    elif mode == "handwriting":
        prompt = f"Rewrite this neatly and clearly:\n\n{content}"
    else:
        prompt = content

    messages = [
        {
            "role": "system",
            "content": "You are Luna, a warm, smart, intuitive assistant. Always answer clearly and helpfully."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    result = ask_ai(messages)
    return {"result": result}


@app.post("/solve-image")
async def solve_image(image: UploadFile = File(...)):
    content = await image.read()
    base64_img = base64.b64encode(content).decode()

    messages = [
        {
            "role": "system",
            "content": "You are Luna, an AI teacher. Explain images step by step, clearly and kindly."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image": base64_img
                }
            ]
        }
    ]

    result = ask_ai(messages)
    return {"result": result}
        
