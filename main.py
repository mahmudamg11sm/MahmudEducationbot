import telebot
from telebot import types
import os
import time
from flask import Flask
from threading import Thread
import requests

# ================= WEB SERVER FOR RENDER =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

# ================= KEEP ALIVE =================
def keep_alive():
    while True:
        try:
            url = os.environ.get("RENDER_EXTERNAL_URL") or "https://mahmudeducationbot.onrender.com"
            requests.get(url)
        except:
            pass
        time.sleep(300)  # ping every 5 min

Thread(target=keep_alive).start()

# ================= BOT CONFIG =================
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise Exception("BOT TOKEN not found in environment variables!")

ADMIN_ID = 6648308251
OWNER_USERNAME = "@MHSM5"

FACEBOOK_LINK = "https://www.facebook.com/share/1DFvMtuJoU/"
TELEGRAM_LINK = "https://t.me/Mahmudsm1"
X_LINK = "https://x.com/Mahmud_sm1"
MY_USERNAME_LINK = "https://t.me/MHSM5"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================= STORAGE =================
all_users = set()
user_state = {}
user_coins = {}

# ================= MENUS =================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🐍 Python Lessons")
    markup.add("⚛ Physics Lessons")
    markup.add("📐 Mathematics Lessons")
    markup.add("🧪 Chemistry Lessons")
    markup.add("💰 My Coins")
    markup.add("🌐 My Links")
    markup.add("ℹ️ About")
    return markup

def links_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📘 Facebook", url=FACEBOOK_LINK))
    markup.add(types.InlineKeyboardButton("📢 Telegram Channel", url=TELEGRAM_LINK))
    markup.add(types.InlineKeyboardButton("🐦 X (Twitter)", url=X_LINK))
    markup.add(types.InlineKeyboardButton("👤 My Username", url=MY_USERNAME_LINK))
    return markup

# ================= LESSON DATA =================
lessons = {
    "python": {
        "intro": [
            {"q": "Python is a ____ ?", "a": "programming language"},
            {"q": "Which keyword prints text?", "a": "print"}
        ],
        "variables": [
            {"q": "x = 5 is called?", "a": "variable"},
            {"q": "Type of 5?", "a": "int"}
        ],
        "loops": [
            {"q": "Which loop repeats?", "a": "for"},
            {"q": "Which loop also repeats?", "a": "while"}
        ]
    },

    "physics": {
        "motion": [
            {"q": "Speed is distance / ____ ?", "a": "time"},
            {"q": "Unit of speed?", "a": "m/s"}
        ],
        "force": [
            {"q": "Force = mass x ____ ?", "a": "acceleration"},
            {"q": "Unit of force?", "a": "newton"}
        ],
        "energy": [
            {"q": "Energy of motion is called?", "a": "kinetic"},
            {"q": "Stored energy is called?", "a": "potential"}
        ]
    },

    "math": {
        "addition": [
            {"q": "10 + 5 = ?", "a": "15"},
            {"q": "7 + 8 = ?", "a": "15"}
        ],
        "multiplication": [
            {"q": "5 x 5 = ?", "a": "25"},
            {"q": "9 x 3 = ?", "a": "27"}
        ],
        "fractions": [
            {"q": "1/2 + 1/2 = ?", "a": "1"},
            {"q": "1/4 + 1/4 = ?", "a": "1/2"}
        ]
    },

    "chemistry": {
        "atoms": [
            {"q": "The smallest unit of matter is?", "a": "atom"},
            {"q": "Center of atom is called?", "a": "nucleus"}
        ],
        "elements": [
            {"q": "H is the symbol of?", "a": "hydrogen"},
            {"q": "O is the symbol of?", "a": "oxygen"}
        ],
        "acids": [
            {"q": "pH of acid is less than?", "a": "7"},
            {"q": "HCl is an example of?", "a": "acid"}
        ]
    }
}

# ================= COMMANDS =================
@bot.message_handler(commands=["start"])
def start(msg):
    chat_id = msg.chat.id
    all_users.add(chat_id)
    if chat_id not in user_coins:
        user_coins[chat_id] = 0
    bot.send_message(chat_id, "Welcome to Education Bot!", reply_markup=main_menu())

# ================= MAIN HANDLER =================
@bot.message_handler(func=lambda m: True)
def handle(msg):
    chat_id = msg.chat.id
    text = msg.text.strip()
    text_low = text.lower()
    all_users.add(chat_id)
    if chat_id not in user_coins:
        user_coins[chat_id] = 0

    # ===== ADMIN BROADCAST =====
    if chat_id == ADMIN_ID and text_low.startswith("/broadcast"):
        msg_text = text.replace("/broadcast", "").strip()
        if not msg_text:
            bot.send_message(chat_id, "Use: /broadcast Your message")
            return
        sent = 0
        for user in all_users:
            try:
                bot.send_message(user, f"📢 Admin Message:\n\n{msg_text}")
                sent += 1
            except:
                pass
        bot.send_message(chat_id, f"Sent to {sent} users.")
        return

    # ===== BUTTONS =====
    if text == "💰 My Coins":
        bot.send_message(chat_id, f"Your coins: {user_coins[chat_id]}")
        return

    if text == "ℹ️ About":
        bot.send_message(chat_id, f"This bot teaches:\nPython, Physics, Mathematics, Chemistry.\n\nOwner: {OWNER_USERNAME}")
        return

    if text == "🌐 My Links":
        bot.send_message(chat_id, "Follow me here:", reply_markup=links_menu())
        return

    if text == "🐍 Python Lessons":
        show_chapters(chat_id, "python"); return
    if text == "⚛ Physics Lessons":
        show_chapters(chat_id, "physics"); return
    if text == "📐 Mathematics Lessons":
        show_chapters(chat_id, "math"); return
    if text == "🧪 Chemistry Lessons":
        show_chapters(chat_id, "chemistry"); return

    # ===== CHAPTER SELECT =====
    if chat_id in user_state and user_state[chat_id]["mode"] == "select_chapter":
        select_chapter(chat_id, text); return

    # ===== QUIZ ANSWER =====
    if chat_id in user_state and user_state[chat_id]["mode"] == "quiz":
        check_answer(chat_id, text_low); return

# ================= CHAPTER SYSTEM =================
def show_chapters(chat_id, subject):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for ch in lessons[subject].keys():
        markup.add(ch.title())
    markup.add("⬅️ Back to Menu")
    user_state[chat_id] = {"mode": "select_chapter", "subject": subject}
    bot.send_message(chat_id, f"Select {subject.title()} Chapter:", reply_markup=markup)

def select_chapter(chat_id, text):
    if text == "⬅️ Back to Menu":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "Main Menu", reply_markup=main_menu())
        return
    subject = user_state[chat_id]["subject"]
    key = text.lower()
    if key not in lessons[subject]:
        bot.send_message(chat_id, "Please select from buttons.")
        return
    user_state[chat_id] = {"mode": "quiz","subject": subject,"chapter": key,"q_index": 0,"fail": 0}
    ask_question(chat_id)

# ================= QUIZ =================
def ask_question(chat_id):
    state = user_state[chat_id]
    qs = lessons[state["subject"]][state["chapter"]]
    if state["q_index"] >= len(qs):
        user_coins[chat_id] += 5
        bot.send_message(chat_id, f"Chapter finished! +5 coins. Total: {user_coins[chat_id]}")
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "Back to menu", reply_markup=main_menu())
        return
    q = qs[state["q_index"]]["q"]
    bot.send_message(chat_id, f"❓ {q}")

def check_answer(chat_id, answer):
    state = user_state[chat_id]
    qs = lessons[state["subject"]][state["chapter"]]
    correct = qs[state["q_index"]]["a"].lower()
    if answer == correct:
        bot.send_message(chat_id, "✅ Correct!")
        state["q_index"] += 1
        state["fail"] = 0
        ask_question(chat_id)
    else:
        state["fail"] += 1
        if state["fail"] >= 3:
            bot.send_message(chat_id, "❌ Skipped!")
            state["q_index"] += 1
            state["fail"] = 0
            ask_question(chat_id)
        else:
            bot.send_message(chat_id, f"❌ Wrong! Try again ({state['fail']}/3)")

# ================= RUN BOT =================
print("Bot is running...")
bot.infinity_polling(skip_pending=True)
