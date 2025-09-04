from fastapi import FastAPI
import requests
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleRequest
from google.cloud import firestore
from datetime import datetime

app = FastAPI()

# Firebase service account file
SERVICE_ACCOUNT_FILE = "service-account.json"
PROJECT_ID = "fir-send-notification-e6a29"

# Load credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/firebase.messaging",
            "https://www.googleapis.com/auth/datastore"]
)

# Firestore client
db = firestore.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)

def get_access_token():
    request = GoogleRequest()
    credentials.refresh(request)
    return credentials.token

# ✅ Helper function: send notification + save in Firestore
async def send_fcm_message(data: dict):
    doctor_token = data.get("doctor_token")
    patient_id = data.get("patient_id")
    patient_name = data.get("patient_name")
    age = data.get("age")
    bp = data.get("bp")
    pulse = data.get("pulse")
    glucose = data.get("glucose")
    temperature = data.get("temperature")

    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    message = {
        "message": {
            "token": doctor_token,
            "notification": {
                "title": f"Health Update for Patient {patient_name},{patient_id}",
                "body": f"Age : {age}, BP: {bp}, Pulse: {pulse}, Glucose: {glucose}, Temp: {temperature}°C"
            },
            "data": {
                "patient_id": str(patient_id),
                "patient_name": str(patient_name),
                "age": str(age),
                "bp": str(bp),
                "pulse": str(pulse),
                "glucose": str(glucose),
                "temperature": str(temperature)
            },
            "android": {
                "priority": "high"
            },
            "apns": {
                "headers": {
                "apns-priority": "10"
            }
            },
            "webpush": {
                "headers": {
                "Urgency": "high"
            }
        }
        }
    }

    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    response = requests.post(url, headers=headers, data=json.dumps(message))

    # ✅ Save to Firestore under "notification" collection
    notification_data = {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "age": age,
        "bp": bp,
        "pulse": pulse,
        "glucose": glucose,
        "temperature": temperature,
        "doctor_token": doctor_token,
        "timestamp": datetime.utcnow()
    }
    db.collection("notification").add(notification_data)

    return {
        "status": response.status_code,
        "response": response.json()
    }

# ✅ Normal endpoint (real data from Postman or sensors)
@app.post("/send-health-data")
async def send_health_data(body: dict):
    return await send_fcm_message(body)

# ✅ Dummy endpoint (hardcoded test data)
@app.get("/send-dummy")
async def send_dummy():
    dummy_data = {
        "doctor_token": "fLKdwLFzZOxz_RkIXf4QHp:APA91bFF7Nq7a_QGVddGuvzXn5RL6k3j121G40tuEgC0teQk3gdX2vnxTOtrlBt4OPSNDeYMFnebOBp7A79AC6qFozK9lbEwjDeRIl9C7NyIqWg8qLQMV6M",  # replace with real doctor token
        "patient_id": "PTEST999",
        "patient_name": "Aman Singh",
        "age":"45",
        "bp": "135/90",
        "pulse": "82",
        "glucose": "115",
        "temperature": "37.5"
    }
    return await send_fcm_message(dummy_data)
