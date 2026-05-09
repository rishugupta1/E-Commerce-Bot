from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# =========================================
# META WHATSAPP CONFIG
# =========================================

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

WHATSAPP_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

# =========================================
# USER STATES
# =========================================

users = {}

# =========================================
# SEND MESSAGE
# =========================================

def send_message(to, message):

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(
        WHATSAPP_URL,
        headers=headers,
        json=payload
    )

    print("MESSAGE STATUS:")
    print(response.text)

# =========================================
# VERIFY WEBHOOK
# =========================================

@app.route("/webhook", methods=["GET"])
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403

# =========================================
# RECEIVE MESSAGES
# =========================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    print("WEBHOOK DATA:")
    print(data)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
         return "OK", 200

        message = value["messages"][0]

        number = message["from"]
        text = message["text"]["body"].strip().lower()

    except Exception as e:
        print("ERROR:", e)
        return "OK", 200

    # =====================================
    # START / MENU
    # =====================================

    if text in ["hi", "hello", "start", "menu"]:

        users[number] = {
            "step": "option"
        }

        send_message(
            number,
            "👋 Welcome to Tech HubX Pvt. Ltd.\n\n"
            "Please choose an option:\n\n"
            "1️⃣ Digital Boards\n"
            "2️⃣ 4K PTZ Camera\n"
            "3️⃣ Full Studio\n"
            "4️⃣ Podcast Setup\n\n"
            "👉 Reply with option number"
        )

        return "OK", 200

    # =====================================
    # CHECK USER
    # =====================================

    if number not in users:

        send_message(
            number,
            "👋 Send *Hi* to start inquiry process."
        )

        return "OK", 200

    user = users[number]

    # =====================================
    # OPTION
    # =====================================

    if user["step"] == "option":

        options = {
            "1": "Digital Boards",
            "2": "4K PTZ Camera",
            "3": "Full Studio",
            "4": "Podcast Setup"
        }

        if text not in options:

            send_message(
                number,
                "❌ Invalid option.\n\n"
                "Please select:\n"
                "1️⃣ Digital Boards\n"
                "2️⃣ 4K PTZ Camera\n"
                "3️⃣ Full Studio\n"
                "4️⃣ Podcast Setup"
            )

            return "OK", 200

        user["service"] = options[text]
        user["step"] = "name"

        send_message(number, "👤 What is your name?")

        return "OK", 200

    # =====================================
    # NAME
    # =====================================

    if user["step"] == "name":

        user["name"] = text.title()
        user["step"] = "location"

        send_message(number, "📍 Where are you located?")

        return "OK", 200

    # =====================================
    # LOCATION
    # =====================================

    if user["step"] == "location":

        user["location"] = text.title()
        user["step"] = "budget"

        send_message(number, "💰 What is your budget?")

        return "OK", 200

    # =====================================
    # BUDGET
    # =====================================

    if user["step"] == "budget":

        user["budget"] = text
        user["step"] = "brand"

        send_message(
            number,
            "🏷 Select Brand:\n\n"
            "1️⃣ TechHub X\n"
            "2️⃣ MaxHub\n"
            "3️⃣ Teachmint X"
        )

        return "OK", 200

    # =====================================
    # BRAND
    # =====================================

    if user["step"] == "brand":

        brands = {
            "1": "TechHub X",
            "2": "MaxHub",
            "3": "Teachmint X"
        }

        if text not in brands:

            send_message(
                number,
                "❌ Invalid brand.\n\n"
                "1️⃣ TechHub X\n"
                "2️⃣ MaxHub\n"
                "3️⃣ Teachmint X"
            )

            return "OK", 200

        user["brand"] = brands[text]
        user["step"] = "timeline"

        send_message(
            number,
            "⏳ Select Timeline:\n\n"
            "1️⃣ 1-3 Days\n"
            "2️⃣ 4-7 Days\n"
            "3️⃣ 7-10 Days\n"
            "4️⃣ 10+ Days"
        )

        return "OK", 200

    # =====================================
    # TIMELINE
    # =====================================

    if user["step"] == "timeline":

        timelines = {
            "1": "1-3 Days",
            "2": "4-7 Days",
            "3": "7-10 Days",
            "4": "10+ Days"
        }

        if text not in timelines:

            send_message(
                number,
                "❌ Invalid timeline.\n\n"
                "1️⃣ 1-3 Days\n"
                "2️⃣ 4-7 Days\n"
                "3️⃣ 7-10 Days\n"
                "4️⃣ 10+ Days"
            )

            return "OK", 200

        user["timeline"] = timelines[text]

        summary = (
            "✅ Inquiry Submitted Successfully\n\n"
            f"📌 Service: {user['service']}\n"
            f"👤 Name: {user['name']}\n"
            f"📍 Location: {user['location']}\n"
            f"💰 Budget: {user['budget']}\n"
            f"🏷 Brand: {user['brand']}\n"
            f"⏳ Timeline: {user['timeline']}\n\n"
            "📞 Our team will contact you soon!"
        )

        send_message(number, summary)

        del users[number]

        return "OK", 200

    return "OK", 200

# =========================================
# RUN SERVER
# =========================================

if __name__ == "__main__":
    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False
    )