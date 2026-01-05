
import requests

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
headers = {
    "x-goog-api-key": "AIzaSyCTS-7Skx19znjFuXeF9i2ayDvCZeWxTis",
    "Content-Type": "application/json"
}

body={
    "contents": [
        {
            "parts": [
                {
                    "text": "Explain how AI works in a few words"
                }
            ]
        }
    ]
}   

res=requests.post(url, headers=headers, json=body)
data=res.json()
data["candidates"][0]["content"]["parts"][0]["text"]

 

