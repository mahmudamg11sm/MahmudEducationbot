import os
import json
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# ================= CONFIG =================
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 6648308251))  # fallback

OWNER_USERNAME = "@MHSM5"
FACEBOOK_LINK = "https://www.facebook.com/share/19iY36vXk9/"
TELEGRAM_LINK = "https://t.me/Mahmudsm1"
X_LINK = "https://x.com/Mahmud_sm1"

COINS_PER_TOPIC = 5
DB_FILE = "db.json"

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================= TELEGRAM BOT =================
bot = telebot.TeleBot(TOKEN)

# ================= DATABASE =================
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_db():
    with open(DB_FILE,"r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE,"w") as f:
        json.dump(db,f)

db = load_db()

# ================= LESSONS =================
lessons = {
    "Python": [
        {"topic": "Variables", "q": [{"q":"Variables store data values. What keyword is used to assign?", "a":"="}]},
        {"topic": "If Statement", "q": [{"q":"If statements make decisions. Example: if x>5:. What is x>5 called?", "a":"condition"}]}
    ],
    "Math": [
        {"topic":"Speed","q":[{"q":"Speed = distance/time. Example: v=d/t. What is v called?","a":"velocity"}]}
    ]
}

user_progress = {}  # chat_id -> {subject, topic_index, q_index, attempts}
user_coins = {}     # chat_id -> coins

# ================= BUTTONS =================
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🐍 Python", "🧮 Math")
    kb.add("💰 My Coins", "ℹ️ About")
    return kb

def about_buttons():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Telegram", url=TELEGRAM_LINK))
    kb.add(types.InlineKeyboardButton("X", url=X_LINK))
    kb.add(types.InlineKeyboardButton("Facebook", url=FACEBOOK_LINK))
    return kb

# ================= FUNCTIONS =================
def ask_question(chat_id):
    progress = user_progress[chat_id]
    subj = progress["subject"]
    topic = lessons[subj][progress["topic_index"]]
    q_data = topic["q"][progress["q_index"]]
    bot.send_message(chat_id, q_data["q"])

# ================= MESSAGE HANDLER =================
@bot.message_handler(func=lambda m: True)
def handle(msg):
    chat_id = msg.chat.id
    text = msg.text.strip()

    # Start subject
    for subj in lessons.keys():
        if subj.lower() in text.lower():
            user_progress[chat_id] = {"subject":subj,"topic_index":0,"q_index":0,"attempts":0}
            ask_question(chat_id)
            return

    # Coins check
    if text == "💰 My Coins":
        coins = user_coins.get(chat_id,0)
        bot.send_message(chat_id,f"💰 You have {coins} coins.")
        return

    # About section
    if text == "ℹ️ About":
        bot.send_message(chat_id,"Owner: "+OWNER_USERNAME, reply_markup=about_buttons())
        return

    # Answer handling
    if chat_id in user_progress:
        progress = user_progress[chat_id]
        subj = progress["subject"]
        topic = lessons[subj][progress["topic_index"]]
        q_data = topic["q"][progress["q_index"]]

        if text.lower() == q_data["a"].lower():
            bot.send_message(chat_id,"✅ Correct! +5 coins")
            user_coins[chat_id] = user_coins.get(chat_id,0)+COINS_PER_TOPIC
            progress["q_index"] +=1
            progress["attempts"]=0
        else:
            progress["attempts"] +=1
            if progress["attempts"] <2:
                bot.send_message(chat_id,"❌ Try again!")
                return
            else:
                bot.send_message(chat_id,f"⚠ Correct answer: {q_data['a']}")
                progress["q_index"] +=1
                progress["attempts"]=0

        # Next topic or finish
        if progress["q_index"] >= len(topic["q"]):
            progress["topic_index"] +=1
            progress["q_index"]=0

        if progress["topic_index"] >= len(lessons[subj]):
            bot.send_message(chat_id,f"✅ You finished all {subj} lessons!", reply_markup=main_menu())
            del user_progress[chat_id]
        else:
            ask_question(chat_id)

# ================= START BOT =================
def run_bot():
    bot.infinity_polling()

if __name__=="__main__":
    Thread(target=run_flask).start()  # Flask server for Render
    Thread(target=run_bot).start()    # Telegram bot polling
