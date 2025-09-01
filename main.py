from fastapi import FastAPI, Request
import requests
import logging
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleRequest

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
DEVICE_TOKEN = "fPaMkdRcEwuPuVTaT8XsaK:APA91bHO6IphE_txNRIiPNPIPFvkz8c9fVS63phOQibHFHrDPLPATu2Jjx7nvg7QHmBbi0UHVDBUoaEkW76BRzlKWqm0ZjlBxePpdYkiPIpK15El6AUy6Uo"

DIRECTUS_URL = "https://firebase-notification.directus.app"
DIRECTUS_TOKEN = "4gFa5biODkz2vhkvnwCxgFl3fmelhXBO"
COLLECTION_NAME = "notification"

# -------------------------------------------------
# Firebase Authentication
# -------------------------------------------------
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
credentials.refresh(GoogleRequest())

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI()

@app.get("/")
def home():
    return "Welcome in Send Notifiaction from Firebase"

@app.get("/home")
def test():
    return "Vinay"

@app.post("/directus-webhook")
async def directus_webhook(request: Request):
    """
    Endpoint for Directus webhook when a new item is added.
    """
    data = await request.json()
    logger.info(f"Webhook received: {data}")

    # Fetch latest item from Directus
    headers_directus = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
    response = requests.get(f"{DIRECTUS_URL}/items/{COLLECTION_NAME}", headers=headers_directus)

    if response.status_code != 200:
        logger.error(f"Error fetching data from Directus: {response.status_code}")
        return {"status": "error", "details": response.text}

    item = response.json()["data"][-1]  # Get latest inserted item
    title = item.get("title", "No Title")
    body = item.get("message", "No Message")

    # Firebase message payload
    message_payload = {
        "message": {
            "token": DEVICE_TOKEN,
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    # Firebase FCM endpoint
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }

    firebase_response = requests.post(url, headers=headers, json=message_payload)

    if firebase_response.status_code == 200:
        logger.info("✅ Notification sent successfully!")
        return {"status": "success", "firebase_response": firebase_response.json()}
    else:
        logger.error(f"❌ Failed to send notification: {firebase_response.status_code}, {firebase_response.text}")
        return {"status": "error", "firebase_response": firebase_response.text}
