from flask import Flask, request
import requests

app = Flask(__name__)

# --- UltraMsg Credentials ---
INSTANCE_ID = "instance165821"   # Replace with your Instance ID
TOKEN = "lo5enfi9dqaldopm"                # Replace with your Token

# --- Send Message Function ---
def send_message(to, message):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    payload = {
        "token": TOKEN,
        "to": to,
        "body": message
    }
    requests.post(url, json=payload)

# --- Menu ---
MENU = """
🍽️ *MUNCHEEZ BISTRO MENU*
━━━━━━━━━━━━━━━━━━━━
🐟 *SEAFOOD*
1. Garlic Butter Jumbo Prawns - Ksh 1,400
2. Grilled Red Snapper - Ksh 1,600
3. Calamari & Squid - Ksh 1,100

🔥 *BBQ & GRILLS*
4. Honey Glazed Pork Ribs - Ksh 1,500
5. Pork Chops Sauté - Ksh 1,200
6. Smoked Beef Brisket - Ksh 1,400

🍗 *CHICKEN*
7. Stuffed Chicken Roulade - Ksh 1,350
8. Butter Chicken - Ksh 1,100
9. Spiced Grilled Wings - Ksh 900

🍟 *SIDES*
10. Loaded Fries - Ksh 650
11. Pilau Rice - Ksh 500
12. Ugali & Sukuma - Ksh 400

🍹 *DRINKS*
13. Signature Cocktails - Ksh 800-1,200
14. Pineapple Mint Juice - Ksh 400
15. Coffee & Tea - Ksh 250-450

🍫 *DESSERTS*
16. Chocolate Lava Cake - Ksh 750
17. Fresh Fruit Platter - Ksh 600
━━━━━━━━━━━━━━━━━━━━
Reply with the *number* to order!
"""

# --- Store user sessions ---
sessions = {}

# --- Webhook ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("body", "").strip().lower()
    sender = data.get("from", "")

    # Ignore messages sent by the bot itself
    if data.get("fromMe"):
        return "ok", 200

    # Get or create session
    if sender not in sessions:
        sessions[sender] = {"state": "start", "order": []}

    session = sessions[sender]
    state = session["state"]

    # --- START / GREETING ---
    if any(word in message for word in ["hi", "hello", "hey", "start", "menu"]):
        session["state"] = "main_menu"
        session["order"] = []
        reply = """👋 *Welcome to Muncheez Bistro!*
🏠 _Home of Spice — Membley, Nairobi_

What would you like to do?

1️⃣ View Menu & Order
2️⃣ Make a Reservation
3️⃣ Our Location
4️⃣ Opening Hours
5️⃣ Contact Us

_Reply with a number to continue_ 👇"""

    # --- MAIN MENU ---
    elif state == "main_menu":
        if message == "1":
            session["state"] = "ordering"
            reply = MENU
        elif message == "2":
            session["state"] = "reservation"
            reply = """📅 *Make a Reservation*
━━━━━━━━━━━━━━━━━━━━
Please provide the following details:

👤 Your name
👥 Number of people
📅 Date & time

_Example: John, 4 people, Saturday 7PM_"""
        elif message == "3":
            session["state"] = "start"
            reply = """📍 *Find Us*
━━━━━━━━━━━━━━━━━━━━
🏢 Total Petrol Station, Membley
🛣️ Northern Bypass Road
📍 Kahawa North, Nairobi

🗺️ Google Maps:
https://www.google.com/maps/search/Muncheez+Bistro+Nairobi

💡 _We're a hidden gem inside the petrol station — worth every second of the search!_"""
        elif message == "4":
            session["state"] = "start"
            reply = """🕐 *Opening Hours*
━━━━━━━━━━━━━━━━━━━━
📅 Monday – Sunday
⏰ 7:00 AM – 10:00 PM

⚠️ _Hours may vary during Eid al-Fitr. Call ahead to confirm._

📞 0726 592 499"""
        elif message == "5":
            session["state"] = "start"
            reply = """📞 *Contact Muncheez Bistro*
━━━━━━━━━━━━━━━━━━━━
📱 Phone & WhatsApp: 0726 592 499
📍 Total Petrol Station, Membley
🌐 Website: https://sammyroland90-dev.github.io/muncheez-bistro/
📸 Instagram: @muncheezbistro
👍 Facebook: Muncheez Bistro"""
        else:
            reply = "Please reply with *1, 2, 3, 4 or 5* to continue. 😊"

    # --- ORDERING ---
    elif state == "ordering":
        menu_items = {
            "1": ("Garlic Butter Jumbo Prawns", 1400),
            "2": ("Grilled Red Snapper", 1600),
            "3": ("Calamari & Squid", 1100),
            "4": ("Honey Glazed Pork Ribs", 1500),
            "5": ("Pork Chops Sauté", 1200),
            "6": ("Smoked Beef Brisket", 1400),
            "7": ("Stuffed Chicken Roulade", 1350),
            "8": ("Butter Chicken", 1100),
            "9": ("Spiced Grilled Wings", 900),
            "10": ("Loaded Fries", 650),
            "11": ("Pilau Rice", 500),
            "12": ("Ugali & Sukuma", 400),
            "13": ("Signature Cocktails", 1000),
            "14": ("Pineapple Mint Juice", 400),
            "15": ("Coffee & Tea", 350),
            "16": ("Chocolate Lava Cake", 750),
            "17": ("Fresh Fruit Platter", 600),
        }
        if message in menu_items:
            item_name, item_price = menu_items[message]
            session["order"].append((item_name, item_price))
            total = sum(p for _, p in session["order"])
            order_list = "\n".join([f"  ✅ {n} - Ksh {p}" for n, p in session["order"]])
            reply = f"""✅ *Added to your order:*
{item_name} - Ksh {item_price}

🛒 *Your order so far:*
{order_list}

💰 *Total: Ksh {total}*
━━━━━━━━━━━━━━━━━━━━
Reply with:
▶️ Another *number* to add more
✅ *done* to confirm order
❌ *cancel* to start over"""

        elif message == "done":
            if session["order"]:
                total = sum(p for _, p in session["order"])
                order_list = "\n".join([f"  • {n} - Ksh {p}" for n, p in session["order"]])
                session["state"] = "confirm_order"
                reply = f"""🎉 *Order Summary*
━━━━━━━━━━━━━━━━━━━━
{order_list}

💰 *Total: Ksh {total}*
━━━━━━━━━━━━━━━━━━━━
Is this correct?
✅ Reply *yes* to confirm
❌ Reply *no* to cancel"""
            else:
                reply = "Your order is empty! Please select items from the menu first. 😊"

        elif message == "cancel":
            session["state"] = "main_menu"
            session["order"] = []
            reply = "❌ Order cancelled. Type *hi* to start again."
        else:
            reply = "Please reply with a *menu number* to add an item, *done* to confirm, or *cancel* to start over. 😊"

    # --- CONFIRM ORDER ---
    elif state == "confirm_order":
        if message == "yes":
            total = sum(p for _, p in session["order"])
            order_list = "\n".join([f"  • {n} - Ksh {p}" for n, p in session["order"]])
            session["state"] = "start"
            session["order"] = []
            reply = f"""🎊 *Order Confirmed!*
━━━━━━━━━━━━━━━━━━━━
{order_list}

💰 *Total: Ksh {total}*
━━━━━━━━━━━━━━━━━━━━
⏱️ Your order will be ready in *20-30 minutes*

📞 For any changes call: *0726 592 499*

Thank you for choosing *Muncheez Bistro!* 🔥
_Home of Spice — Membley, Nairobi_"""
        elif message == "no":
            session["state"] = "main_menu"
            session["order"] = []
            reply = "❌ Order cancelled. Type *hi* to start again."
        else:
            reply = "Please reply *yes* to confirm or *no* to cancel. 😊"

    # --- RESERVATION ---
    elif state == "reservation":
        session["state"] = "start"
        reply = f"""✅ *Reservation Request Received!*
━━━━━━━━━━━━━━━━━━━━
📋 Details: _{message}_

Our team will confirm your reservation shortly.
📞 For urgent bookings call: *0726 592 499*

See you at *Muncheez Bistro!* 🎉"""

    # --- DEFAULT ---
    else:
        session["state"] = "main_menu"
        reply = """👋 *Welcome to Muncheez Bistro!*
🏠 _Home of Spice — Membley, Nairobi_

What would you like to do?

1️⃣ View Menu & Order
2️⃣ Make a Reservation
3️⃣ Our Location
4️⃣ Opening Hours
5️⃣ Contact Us

_Reply with a number to continue_ 👇"""

    send_message(sender, reply)
    return "ok", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)