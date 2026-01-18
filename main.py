# ======================== main.py ========================
import os
from flask import Flask, request
import telebot

# ================== CONFIG ==================
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 6648308251
OWNER_USERNAME = "@MHSM5"

FACEBOOK_LINK = "https://www.facebook.com/share/1DFvMtuJoU/"
TELEGRAM_LINK = "https://t.me/Mahmudsm1"
X_LINK = "https://x.com/Mahmud_sm1"
MY_USERNAME_LINK = "https://t.me/MHSM5"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

all_users = set()
user_state = {}
user_coins = {}

# ================== KEYBOARDS ==================
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🐍 Python Lessons")],
            [KeyboardButton(text="⚛ Physics Lessons")],
            [KeyboardButton(text="📐 Mathematics Lessons")],
            [KeyboardButton(text="🧪 Chemistry Lessons")],
            [KeyboardButton(text="💰 My Coins")],
            [KeyboardButton(text="🌐 My Links")],
            [KeyboardButton(text="ℹ️ About")]
        ],
        resize_keyboard=True
    )

def links_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 Facebook", url=FACEBOOK_LINK)],
        [InlineKeyboardButton(text="📢 Telegram Channel", url=TELEGRAM_LINK)],
        [InlineKeyboardButton(text="🐦 X (Twitter)", url=X_LINK)],
        [InlineKeyboardButton(text="👤 My Username", url=MY_USERNAME_LINK)]
    ])

# ================== LESSON DATA ==================
lessons = {
    "python": {
        "Basics": [
            {"q": "Python is a ____ ?", "a": "programming language"},
            {"q": "Which keyword prints text?", "a": "print"}
        ],
        "Variables": [
            {"q": "x = 5 is called?", "a": "variable"},
            {"q": "Type of 5?", "a": "int"}
        ]
    },
    "physics": {
        "Motion": [
            {"q": "Speed is distance / ____ ?", "a": "time"},
            {"q": "Unit of speed?", "a": "m/s"}
        ],
        "Force": [
            {"q": "Force = mass x ____ ?", "a": "acceleration"},
            {"q": "Unit of force?", "a": "newton"}
        ]
    },
    "math": {
        "Addition": [
            {"q": "10 + 5 = ?", "a": "15"},
            {"q": "7 + 8 = ?", "a": "15"}
        ],
        "Multiplication": [
            {"q": "5 x 5 = ?", "a": "25"},
            {"q": "9 x 3 = ?", "a": "27"}
        ]
    },
    "chemistry": {
        "Atoms": [
            {"q": "The smallest unit of matter is?", "a": "atom"},
            {"q": "Center of atom is called?", "a": "nucleus"}
        ],
        "Elements": [
            {"q": "H is the symbol of?", "a": "hydrogen"},
            {"q": "O is the symbol of?", "a": "oxygen"}
        ]
    }
}

# ================== HELPER FUNCTIONS ==================
def show_chapters(chat_id, subject):
    chapters = lessons[subject].keys()
    keyboard = [[KeyboardButton(text=ch)] for ch in chapters]
    keyboard.append([KeyboardButton(text="⬅️ Back to Menu")])
    user_state[chat_id] = {"mode": "select_chapter", "subject": subject}
    bot.send_message(chat_id, f"Select {subject.title()} Chapter:", reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))

def select_chapter(chat_id, text):
    if text == "⬅️ Back to Menu":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "Main Menu", reply_markup=main_menu())
        return
    state = user_state[chat_id]
    subject = state["subject"]
    key = text
    if key not in lessons[subject]:
        bot.send_message(chat_id, "Please select from the buttons.")
        return
    user_state[chat_id] = {"mode": "quiz", "subject": subject, "chapter": key, "q_index": 0, "fail": 0}
    ask_question(chat_id)

def ask_question(chat_id):
    state = user_state[chat_id]
    subject = state["subject"]
    chapter = state["chapter"]
    qs = lessons[subject][chapter]
    if state["q_index"] >= len(qs):
        user_coins[chat_id] = user_coins.get(chat_id,0) + 5
        bot.send_message(chat_id, f"Chapter finished! +5 coins. Total: {user_coins[chat_id]}")
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "Back to menu", reply_markup=main_menu())
        return
    q = qs[state["q_index"]]["q"]
    bot.send_message(chat_id, f"Question: {q}")

def check_answer(chat_id, answer):
    state = user_state[chat_id]
    subject = state["subject"]
    chapter = state["chapter"]
    qs = lessons[subject][chapter]
    correct = qs[state["q_index"]]["a"].lower()
    if answer.lower() == correct:
        bot.send_message(chat_id, "Correct!")
        state["q_index"] += 1
        state["fail"] = 0
        ask_question(chat_id)
    else:
        state["fail"] += 1
        if state["fail"] >= 2:
            bot.send_message(chat_id, f"Failed this question twice. Skipping...")
            state["q_index"] += 1
            state["fail"] = 0
            ask_question(chat_id)
        else:
            bot.send_message(chat_id, f"Wrong! Try again ({state['fail']}/2)")

# ================== TELEGRAM HANDLER ==================
@bot.message_handler(func=lambda msg: True)
def handle(msg):
    chat_id = msg.chat.id
    text = msg.text.strip()
    all_users.add(chat_id)
    if chat_id not in user_coins:
        user_coins[chat_id] = 0

    if chat_id == ADMIN_ID and text.startswith("/broadcast"):
        msg_text = text.replace("/broadcast","").strip()
        if not msg_text:
            bot.send_message(chat_id, "Use: /broadcast Your message")
            return
        sent = 0
        for user in all_users:
            try:
                bot.send_message(user, f"Admin Broadcast:\n{msg_text}")
                sent +=1
            except:
                continue
        bot.send_message(chat_id, f"Sent to {sent} users.")
        return

    if text == "/start":
        bot.send_message(chat_id, "Welcome to Education Bot!", reply_markup=main_menu())
        return
    if text == "💰 My Coins":
        bot.send_message(chat_id, f"Your coins: {user_coins[chat_id]}")
        return
    if text == "ℹ️ About":
        bot.send_message(chat_id, f"This bot helps users learn Python, Physics, Math, Chemistry.\nOwner: {OWNER_USERNAME}")
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

    if chat_id in user_state:
        mode = user_state[chat_id]["mode"]
        if mode == "select_chapter":
            select_chapter(chat_id, text)
        elif mode == "quiz":
            check_answer(chat_id, text)

# ================== FLASK WEBHOOK ==================
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def index():
    return "Education Bot is live!", 200

# ================== WEBHOOK SETUP ==================
bot.remove_webhook()
WEBHOOK_URL = f"https://mahmudeducationbot.onrender.com/{TOKEN}"
bot.set_webhook(url=WEBHOOK_URL)

print("Education Bot 3.0 running...")
# ================== RUN FLASK ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
