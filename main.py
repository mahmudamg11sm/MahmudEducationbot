import os
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
TOKEN = os.environ.get("TOKEN")  # Telegram Bot Token from ENV
ADMIN_ID = int(os.environ.get("ADMIN_ID", 6648308251))  # Your Telegram ID

OWNER_USERNAME = "@MHSM5"  # Your Telegram username

# Links
FACEBOOK_LINK = "https://www.facebook.com/share/19iY36vXk9/"
TELEGRAM_LINK = "https://t.me/Mahmudsm1"
X_LINK = "https://x.com/Mahmud_sm1"
MY_USERNAME_LINK = "https://t.me/Mahmudsm1"

# ================= INIT =================
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================= DATA =================
all_users = set()
user_coins = {}
user_progress = {}  # chat_id -> {"subject": "", "topic_index": 0, "q_index": 0, "attempts": 0}

# ================= LESSONS =================
lessons = {
    "python": [
        {"topic": "Basics", "q": [
            {"q": "Python is a ____ ?", "a": "programming language"},
            {"q": "Which keyword prints text?", "a": "print"}
        ]},
        {"topic": "Variables", "q": [
            {"q": "Variables store ___ ?", "a": "data"},
            {"q": "Which symbol is used for comments?", "a": "#"}
        ]}
    ],
    "physics": [
        {"topic": "Motion", "q":[
            {"q": "Speed = distance / ____ ?", "a": "time"},
            {"q": "Unit of speed?", "a": "m/s"}
        ]}
    ],
    "math": [
        {"topic": "Addition", "q":[
            {"q": "10 + 5 = ?", "a": "15"},
            {"q": "7 + 8 = ?", "a": "15"}
        ]}
    ],
    "chemistry": [
        {"topic": "Atoms", "q":[
            {"q": "Smallest unit of matter?", "a": "atom"},
            {"q": "Center of atom?", "a": "nucleus"}
        ]}
    ]
}

# ================= KEYBOARDS =================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("🐍 Python Lessons"), KeyboardButton("⚛ Physics Lessons")],
            [KeyboardButton("📐 Math Lessons"), KeyboardButton("🧪 Chemistry Lessons")],
            [KeyboardButton("💰 My Coins"), KeyboardButton("🏆 Leaderboard")],
            [KeyboardButton("🌐 My Links"), KeyboardButton("ℹ️ About")]
        ], resize_keyboard=True
    )

def links_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📘 Facebook", url=FACEBOOK_LINK))
    markup.add(InlineKeyboardButton("📢 Telegram", url=TELEGRAM_LINK))
    markup.add(InlineKeyboardButton("🐦 X", url=X_LINK))
    markup.add(InlineKeyboardButton("👤 My Profile", url=MY_USERNAME_LINK))
    return markup

# ================= WEBHOOK =================
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "!", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is live!"

bot.remove_webhook()
bot.set_webhook(url=f"https://mahmudeducationbot.onrender.com/{TOKEN}")

# ================= HELPERS =================
def ask_question(chat_id):
    progress = user_progress[chat_id]
    subj = progress["subject"]
    topic = lessons[subj][progress["topic_index"]]
    q_data = topic["q"][progress["q_index"]]
    bot.send_message(chat_id, q_data["q"])

# ================= HANDLERS =================
@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    all_users.add(chat_id)
    if chat_id not in user_coins:
        user_coins[chat_id] = 0
    bot.send_message(chat_id, f"Welcome to Education Bot!\nOwner: {OWNER_USERNAME}", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle(msg):
    chat_id = msg.chat.id
    text = msg.text.lower()
    
    # Coins
    if text == "💰 my coins":
        bot.send_message(chat_id, f"Your coins: {user_coins.get(chat_id,0)}")
        return
    
    # Leaderboard
    if text == "🏆 leaderboard":
        if not user_coins:
            bot.send_message(chat_id, "No leaderboard data yet.")
            return
        leaderboard = sorted(user_coins.items(), key=lambda x: x[1], reverse=True)
        msg_text = "🏆 Leaderboard:\n"
        for i, (uid, coins) in enumerate(leaderboard[:10], 1):
            msg_text += f"{i}. User {uid}: {coins} coins\n"
        bot.send_message(chat_id, msg_text)
        return
    
    # Lessons
    for subj in lessons.keys():
        if subj in text:
            user_progress[chat_id] = {"subject": subj, "topic_index": 0, "q_index": 0, "attempts": 0}
            ask_question(chat_id)
            return

    # Answer handling
    if chat_id in user_progress:
        progress = user_progress[chat_id]
        subj = progress["subject"]
        topic = lessons[subj][progress["topic_index"]]
        q_data = topic["q"][progress["q_index"]]

        if text == q_data["a"].lower():
            bot.send_message(chat_id, "✅ Correct!")
            progress["q_index"] += 1
            progress["attempts"] = 0
            user_coins[chat_id] = user_coins.get(chat_id,0) + 1
        else:
            progress["attempts"] += 1
            if progress["attempts"] < 2:
                bot.send_message(chat_id, "❌ Try again!")
                return
            else:
                bot.send_message(chat_id, f"⚠ Correct answer: {q_data['a']}")
                progress["q_index"] += 1
                progress["attempts"] = 0

        # Next question or topic
        if progress["q_index"] >= len(topic["q"]):
            progress["topic_index"] += 1
            progress["q_index"] = 0
        if progress["topic_index"] >= len(lessons[subj]):
            bot.send_message(chat_id, f"{subj.capitalize()} lessons completed!", reply_markup=main_menu())
            del user_progress[chat_id]
        else:
            ask_question(chat_id)
        return

    # Links
    if text == "🌐 my links":
        bot.send_message(chat_id, "Here are some useful links:", reply_markup=links_keyboard())
        return
    
    # About
    if text == "ℹ️ about":
        bot.send_message(chat_id, f"This bot teaches Python, Physics, Math, Chemistry.\nOwner: {OWNER_USERNAME}", reply_markup=main_menu())
        return
    
    # Default
    bot.send_message(chat_id, "Select an option from menu", reply_markup=main_menu())

# ================= ADMIN BROADCAST =================
@bot.message_handler(commands=['broadcast'])
def broadcast(msg):
    if msg.chat.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "You are not authorized.")
        return
    bot.send_message(msg.chat.id, "Send me the message to broadcast...")
    
    @bot.message_handler(func=lambda m: True)
    def send_broadcast(m):
        for uid in all_users:
            bot.send_message(uid, f"📢 Broadcast:\n{m.text}")
        bot.send_message(ADMIN_ID, "Broadcast sent!")

# ================= RUN FLASK =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
