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
    # AUTO START FOR NEW USER
    # =====================================

    if number not in users:

        users[number] = {
            "step": "option"
        }

        send_message(
            number,
            "👋 Welcome to Balaji LNS IT Solutions\n\n"
            "Please choose an option:\n\n"
            "1️⃣ Digital Boards\n"
            "2️⃣ 4K PTZ Camera\n"
            "3️⃣ Full Studio\n"
            "4️⃣ Podcast Setup\n\n"
            "👉 Reply with option number or name"
        )

        return "OK", 200

    user = users[number]


    # =====================================
    # BACK BUTTON
    # =====================================

    if text in ["back", "previous"]:

        # NAME -> OPTION
        if user["step"] == "name":

            user["step"] = "option"

            send_message(
                number,
                "🔙 Back to Options\n\n"
                "1️⃣ Digital Boards\n"
                "2️⃣ 4K PTZ Camera\n"
                "3️⃣ Full Studio\n"
                "4️⃣ Podcast Setup\n"
                "👉 Type 'back' or 'previous' to go previous step"
            )

            return "OK", 200

        # LOCATION -> NAME
        elif user["step"] == "location":

            user["step"] = "name"

            send_message(
                number,
                "🔙 Enter your name again:\n"
                "👉 Type 'back' or 'previous' to go previous step"
            )

            return "OK", 200

        # BUDGET -> LOCATION
        elif user["step"] == "budget":

            user["step"] = "location"

            send_message(
                number,
                "🔙 Enter your location again:\n"
                "👉 Type 'back' or 'previous' to go previous step"
            )

            return "OK", 200

        # BRAND -> BUDGET
        elif user["step"] == "brand":

            user["step"] = "budget"

            send_message(
                number,
                "🔙 Enter your budget again:\n"
                "👉 Type 'back' or 'previous' to go previous step"
            )

            return "OK", 200

        # TIMELINE -> BRAND
        elif user["step"] == "timeline":

            user["step"] = "brand"

            send_message(
                number,
                "🔙 Select Brand Again:\n\n"
                "1️⃣ TechHub X\n"
                "2️⃣ MaxHub\n"
                "3️⃣ Teachmint X\n"
            "👉 Type 'back' or 'previous' to go previous step"
            )

            return "OK", 200
    # =====================================
    # OPTION
    # =====================================

    @app.route("/webhook", methods=["POST"])
    def webhook():
    # =====================================
    # NAME
    # =====================================
 
     if user["step"] == "name":

        user["name"] = text.title()
        user["step"] = "location"

        send_message(number, "📍 Where are you located?\n"
            "👉 Type 'back' or 'previous' to go previous step")

        return "OK", 200

    # =====================================
    # LOCATION
    # =====================================

    if user["step"] == "location":

        user["location"] = text.title()
        user["step"] = "budget"

        send_message(number, "💰 What is your budget?\n"
            "👉 Type 'back' or 'previous' to go previous step")

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
            "3️⃣ Teachmint X\n"
            "👉 Type 'back' or 'previous' to go previous step"
        )

        return "OK", 200

    # =====================================
    # BRAND
    # =====================================

    if user["step"] == "brand":

        # TECHHUB X
        if text in [
            "1",
            "techhub",
            "tech hub",
            "techhub x",
            "techhubx",
            "hub",
            "tech",
            "hubx"
        ]:

            user["brand"] = "TechHub X"

        # MAXHUB
        elif text in [
            "2",
            "maxhub",
            "max hub",
            "max"
        ]:

            user["brand"] = "MaxHub"

        # TEACHMINT X
        elif text in [
            "3",
            "teachmint",
            "teach mint",
            "teachmint x",
            "teachmintx"
        ]:

            user["brand"] = "Teachmint X"

        # ANY OTHER BRAND
        else:

            user["brand"] = text.title()

        # NEXT STEP
        user["step"] = "timeline"

        send_message(
            number,
            "⏳ Select Timeline:\n\n"
            "1️⃣ 1-3 Days\n"
            "2️⃣ 4-7 Days\n"
            "3️⃣ 7-10 Days\n"
            "4️⃣ 10+ Days\n\n"
            "👉 Or type your own timeline\n"
            "👉 Type 'back' or 'previous' to go previous step"
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
                "4️⃣ 10+ Days\n"
            "👉 Type 'back' or 'previous' to go previous step"
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