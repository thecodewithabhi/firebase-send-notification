from flask import Flask, request
import firebase_admin
from firebase_admin import messaging, credentials

app = Flask(__name__)

# Load Firebase credentials
cred = credentials.Certificate("service-account.json")  # Your service account JSON
firebase_admin.initialize_app(cred)

@app.route('/directus-webhook', methods=['POST'])
def notify():
    data = request.json.get("payload", {})  # Directus sends the payload here

    title = data.get("title", "No Title")
    body = data.get("message", "No Message")
    target = data.get("target")
    token = data.get("device_token")

    print(f"Received notification: {title}, {body}, {target}, {token}")

    # Build Firebase message
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token
    )

    try:
        response = messaging.send(message)
        return {"success": True, "firebase_response": response}, 200
    except Exception as e:
        print("Error sending Firebase message:", str(e))
        return {"success": False, "error": str(e)}, 500

if __name__ == "__main__":
    app.run(port=5000)
