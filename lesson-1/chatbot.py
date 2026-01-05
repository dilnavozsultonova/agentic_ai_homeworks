import json
import os

HISTORY_FILE="chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return []

from dotenv import load_dotenv
load_dotenv('.env')

from google import genai

client = genai.Client()

history = load_history()

def save_history(history):
    with open(HISTORY_FILE,"w",encoding="utf-8")as f:
        json.dump(history,f,ensure_ascii=False,indent=2)

while True:
    user_input=input("User: ")
    history.append({"role": "user", "content": user_input})
    prompt = " "
    for message in history:
        role = message["role"]
        content = message["content"]
        if role=="user":
            prompt += f"User: {content}\n"
        else:
            prompt += f"AI: {content}\n"
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
        )
    print("AI:", response.text)
    history.append({"role": "assistant", "content": response.text})
    save_history(history)

