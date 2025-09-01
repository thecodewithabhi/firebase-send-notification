from fastapi import FastAPI, Request
import firebase_admin
from firebase_admin import credentials, messaging
import json

# Initialize Firebase Admin SDK
cred = credentials.Certificate("service-account.json")
firebase_admin.initialize_app(cred)

app = FastAPI()

@app.get('/')
def home():
    return "Welcome in the Project - Based on send notification from firebase"

@app.get('/home')
def home():
    return "Welcome in the Project"

@app.post("/directus-webhook")
async def directus_webhook(request: Request):
    data = await request.json()
    print("Webhook received:", data)

    # Example: send notification when a new item is created
    title = data.get("title", "New Update")
    body = data.get("body", "Something changed in Directus!")

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic="news",  # OR use token="DEVICE_FCM_TOKEN"
    )

    response = messaging.send(message)
    print("Sent message:", response)

    return {"status": "Notification sent", "id": response}
