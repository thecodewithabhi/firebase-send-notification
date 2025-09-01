from flask import Flask, request, jsonify
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

app = Flask(__name__)

# Firebase setup
SERVICE_ACCOUNT_FILE = 'service-account.json'
PROJECT_ID = 'fir-send-notification-e6a29'

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.json
    print("🔔 Incoming Webhook Data:", data)

    title = data.get("title", "No Title")
    message = data.get("message", "No Message")
    target = data.get("target", "")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )
    credentials.refresh(Request())

    payload = {
        "message": {
            "notification": {
                "title": title,
                "body": message
            }
        }
    }

    if target.startswith("APA91"):
        payload["message"]["token"] = target
    else:
        payload["message"]["topic"] = target

    firebase_url = f'https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send'
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }

    response = requests.post(firebase_url, headers=headers, json=payload)

    if response.status_code == 200:
        return jsonify({"status": "success", "firebase_response": response.json()})
    else:
        return jsonify({"status": "error", "firebase_response": response.text}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
