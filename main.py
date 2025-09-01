from fastapi import FastAPI, Request
import requests
import logging
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleRequest
from google.cloud import firestore

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Configurations
# -------------------------------------------------
SERVICE_ACCOUNT_FILE = "service-account.json"
PROJECT_ID = "fir-send-notification-e6a29"

# -------------------------------------------------
# Firebase Authentication for FCM
# -------------------------------------------------
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

def get_access_token():
    credentials.refresh(GoogleRequest())
    return credentials.token

# -------------------------------------------------
# Firestore Client
# -------------------------------------------------
firestore_client = firestore.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to Send Notification from Firebase"}

@app.post("/directus-webhook")
async def directus_webhook(request: Request):
    """
    Endpoint for Directus webhook when a new item is added.
    """
    data = await request.json()
    logger.info(f"Webhook received: {data}")

    # Extract fields directly from webhook payload
    device_token = data.get("device_token")
    title = data.get("title", "No Title")
    body = data.get("message", "No Message")

    if not device_token:
        logger.error("❌ No device token found in webhook payload")
        return {"status": "error", "details": "No device token provided"}

    # Firebase message payload
    message_payload = {
        "message": {
            "token": device_token,
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    # Firebase FCM endpoint
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }

    firebase_response = requests.post(url, headers=headers, json=message_payload)

    if firebase_response.status_code == 200:
        logger.info("✅ Notification sent successfully!")

        # Save notification into Firestore
        firestore_client.collection("notification").add({
            "title": title,
            "message": body
        })

        return {"status": "success", "firebase_response": firebase_response.json()}
    else:
        logger.error(f"❌ Failed to send notification: {firebase_response.status_code}, {firebase_response.text}")
        return {"status": "error", "firebase_response": firebase_response.text}
