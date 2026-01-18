import os
import json
from flask import Flask, request
import telebot
from telebot import types

# ================== CONFIG ==================
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

WEBHOOK_URL = "https://mahmudeducationbot.onrender.com/"

DB_FILE = "db.json"
COINS_PER_TOPIC = 5

OWNER_USERNAME = "@MHSM5"

# ================== FLASK ==================
app = Flask(__name__)

# ================== TELEGRAM BOT ==================
bot = telebot.TeleBot(TOKEN, threaded=False)

# ================== WEBHOOK SETUP ==================
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# ================== DATABASE ==================
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"coins": {}}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db = load_db()
user_coins = db.get("coins", {})
user_progress = {}

# ================== LESSONS ==================
lessons = {
    "Python": [
        {
            "topic": "Variables",
            "q": [
                {"q": "Which symbol is used to assign value in Python?", "a": "="},
                {"q": "x = 5, what is x?", "a": "5"},
            ]
        },
        {
            "topic": "Print",
            "q": [
                {"q": "Which function prints in Python?", "a": "print"},
            ]
        }
    ],
    "Math": [
        {
            "topic": "Speed",
            "q": [
                {"q": "v = d / t, what is v?", "a": "velocity"},
            ]
        }
    ]
}

# ================== KEYBOARDS ==================
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🐍 Python", "🧮 Math")
    kb.add("💰 My Coins", "🏆 Leaderboard")
    kb.add("ℹ️ About")
    return kb

def about_buttons():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Telegram", url="https://t.me/Mahmudsm1"))
    kb.add(types.InlineKeyboardButton("X", url="https://x.com/Mahmud_sm1"))
    kb.add(types.InlineKeyboardButton("Facebook", url="https://www.facebook.com/share/19iY36vXk9/"))
    return kb

# ================== FUNCTIONS ==================
def ask_question(chat_id):
    p = user_progress[chat_id]
    topic = lessons[p["subject"]][p["topic_index"]]
    q_data = topic["q"][p["q_index"]]
    bot.send_message(chat_id, f"📘 {topic['topic']}\n\n❓ {q_data['q']}")

def show_leaderboard(chat_id):
    if not user_coins:
        bot.send_message(chat_id, "No data yet.")
        return
    sorted_users = sorted(user_coins.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 Leaderboard:\n\n"
    for i, (uid, coins) in enumerate(sorted_users[:10], start=1):
        text += f"{i}. User {uid} — {coins} coins\n"
    bot.send_message(chat_id, text)

# ================== HANDLERS ==================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, "👋 Welcome to Mahmud Education Bot!\nChoose a subject:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle(msg):
    chat_id = msg.chat.id
    text = msg.text.strip()

    # SUBJECTS
    if "python" in text.lower():
        user_progress[chat_id] = {"subject": "Python", "topic_index": 0, "q_index": 0, "attempts": 0}
        ask_question(chat_id)
        return

    if "math" in text.lower():
        user_progress[chat_id] = {"subject": "Math", "topic_index": 0, "q_index": 0, "attempts": 0}
        ask_question(chat_id)
        return

    # COINS
    if text == "💰 My Coins":
        bot.send_message(chat_id, f"💰 You have {user_coins.get(str(chat_id), 0)} coins.")
        return

    # LEADERBOARD
    if text == "🏆 Leaderboard":
        show_leaderboard(chat_id)
        return

    # ABOUT
    if text == "ℹ️ About":
        bot.send_message(chat_id, f"Owner: {OWNER_USERNAME}", reply_markup=about_buttons())
        return

    # ANSWERS
    if chat_id in user_progress:
        p = user_progress[chat_id]
        topic = lessons[p["subject"]][p["topic_index"]]
        q_data = topic["q"][p["q_index"]]

        if text.lower() == q_data["a"].lower():
            bot.send_message(chat_id, "✅ Correct! +5 coins")
            uid = str(chat_id)
            user_coins[uid] = user_coins.get(uid, 0) + COINS_PER_TOPIC
            save_db({"coins": user_coins})

            p["q_index"] += 1
            p["attempts"] = 0
        else:
            p["attempts"] += 1
            if p["attempts"] < 2:
                bot.send_message(chat_id, "❌ Try again!")
                return
            else:
                bot.send_message(chat_id, f"⚠ Correct answer: {q_data['a']}")
                p["q_index"] += 1
                p["attempts"] = 0

        if p["q_index"] >= len(topic["q"]):
            p["topic_index"] += 1
            p["q_index"] = 0

        if p["topic_index"] >= len(lessons[p["subject"]]):
            bot.send_message(chat_id, f"🎉 You finished all {p['subject']} lessons!", reply_markup=main_menu())
            del user_progress[chat_id]
        else:
            ask_question(chat_id)

# ================== FLASK ROUTES ==================
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# ================== RUN ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
