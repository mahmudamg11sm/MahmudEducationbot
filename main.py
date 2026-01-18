import os
from flask import Flask, request, jsonify, render_template_string
import telebot

# ================== CONFIG ==================
TOKEN = os.environ.get("TOKEN")  # Telegram bot token
ADMIN_ID = 6648308251            # Your Telegram ID
OWNER_USERNAME = "@MHSM5"

FACEBOOK_LINK = "https://www.facebook.com/share/1DFvMtuJoU/"
TELEGRAM_LINK = "https://t.me/Mahmudsm1"
X_LINK = "https://x.com/Mahmud_sm1"
MY_USERNAME_LINK = "https://t.me/MHSM5"
# ===========================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ====== In-memory database ======
all_users = set()
user_coins = {}
user_state = {}

# ====== Keyboards ======
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("🐍 Python Lessons"), KeyboardButton("⚛ Physics Lessons")],
            [KeyboardButton("📐 Mathematics Lessons"), KeyboardButton("🧪 Chemistry Lessons")],
            [KeyboardButton("💰 My Coins")],
            [KeyboardButton("🌐 My Links"), KeyboardButton("ℹ️ About")]
        ],
        resize_keyboard=True
    )

def links_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 Facebook", url=FACEBOOK_LINK)],
        [InlineKeyboardButton("📢 Telegram", url=TELEGRAM_LINK)],
        [InlineKeyboardButton("🐦 X", url=X_LINK)],
        [InlineKeyboardButton("👤 My Username", url=MY_USERNAME_LINK)]
    ])

# ====== Extended Lessons ======
lessons = {
    "python": {
        "basics": [
            {"q": "Python is a ____ ?", "a": "programming language"},
            {"q": "Which keyword prints text?", "a": "print"},
            {"q": "How do you create a variable x with value 5?", "a": "x=5"}
        ],
        "loops": [
            {"q": "Which loop repeats while a condition is True?", "a": "while"},
            {"q": "Which loop repeats a fixed number of times?", "a": "for"}
        ],
        "functions": [
            {"q": "Define a function named 'hello'?", "a": "def hello():"},
            {"q": "How to return value 10?", "a": "return 10"}
        ]
    },
    "physics": {
        "motion": [
            {"q": "Speed = distance / ____ ?", "a": "time"},
            {"q": "Unit of speed?", "a": "m/s"},
            {"q": "Acceleration formula?", "a": "change in velocity/time"}
        ],
        "force": [
            {"q": "F = m * ____ ?", "a": "a"},
            {"q": "Unit of force?", "a": "newton"}
        ]
    },
    "math": {
        "addition": [
            {"q": "10 + 5 = ?", "a": "15"},
            {"q": "7 + 8 = ?", "a": "15"}
        ],
        "subtraction": [
            {"q": "20 - 5 = ?", "a": "15"},
            {"q": "15 - 7 = ?", "a": "8"}
        ],
        "multiplication": [
            {"q": "5 * 3 = ?", "a": "15"},
            {"q": "7 * 2 = ?", "a": "14"}
        ]
    },
    "chemistry": {
        "atoms": [
            {"q": "Smallest unit of matter?", "a": "atom"},
            {"q": "Center of atom is called?", "a": "nucleus"}
        ],
        "elements": [
            {"q": "H is the symbol for?", "a": "hydrogen"},
            {"q": "O is the symbol for?", "a": "oxygen"}
        ],
        "reactions": [
            {"q": "Combustion reaction needs ____ ?", "a": "oxygen"},
            {"q": "Na + Cl -> ?", "a": "NaCl"}
        ]
    }
}

# ====== Bot Handlers ======
@bot.message_handler(func=lambda m: True)
def handle(msg):
    chat_id = msg.chat.id
    text = msg.text.strip()
    all_users.add(chat_id)
    if chat_id not in user_coins:
        user_coins[chat_id] = 0
    text_low = text.lower()

    # ---- Admin broadcast ----
    if chat_id == ADMIN_ID and text_low.startswith("/broadcast"):
        msg_text = text.replace("/broadcast", "").strip()
        for u in all_users:
            try:
                bot.send_message(u, f"Admin Broadcast:\n{msg_text}")
            except: pass
        bot.send_message(chat_id, f"Broadcast sent to {len(all_users)} users.")
        return

    # ---- /start ----
    if text_low == "/start":
        bot.send_message(chat_id, "Welcome to Education Bot!", reply_markup=main_menu())
        return

    # ---- Coins ----
    if text == "💰 My Coins":
        bot.send_message(chat_id, f"Your coins: {user_coins[chat_id]}")
        return

    # ---- About ----
    if text == "ℹ️ About":
        bot.send_message(chat_id,
            f"This bot teaches Python, Physics, Math, Chemistry.\nOwner: {OWNER_USERNAME}"
        )
        return

    # ---- Links ----
    if text == "🌐 My Links":
        bot.send_message(chat_id, "Follow me here:", reply_markup=links_menu())
        return

    # ---- Lessons ----
    subjects = {
        "🐍 Python Lessons": "python",
        "⚛ Physics Lessons": "physics",
        "📐 Mathematics Lessons": "math",
        "🧪 Chemistry Lessons": "chemistry"
    }
    if text in subjects:
        show_chapters(chat_id, subjects[text])
        return

    # ---- Chapter select ----
    if chat_id in user_state and user_state[chat_id]["mode"] == "select_chapter":
        select_chapter(chat_id, text)
        return

    # ---- Quiz ----
    if chat_id in user_state and user_state[chat_id]["mode"] == "quiz":
        check_answer(chat_id, text_low)
        return

# ====== Chapter system ======
def show_chapters(chat_id, subject):
    keyboard = [[KeyboardButton(ch.title())] for ch in lessons[subject].keys()]
    keyboard.append([KeyboardButton("⬅️ Back to Menu")])
    user_state[chat_id] = {"mode":"select_chapter","subject":subject}
    bot.send_message(chat_id, f"Select {subject.title()} chapter:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

def select_chapter(chat_id, text):
    if text == "⬅️ Back to Menu":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "Main Menu", reply_markup=main_menu())
        return
    state = user_state[chat_id]
    subject = state["subject"]
    key = text.lower()
    if key not in lessons[subject]:
        bot.send_message(chat_id, "Please select from buttons.")
        return
    user_state[chat_id] = {"mode":"quiz","subject":subject,"chapter":key,"q_index":0,"fail":0}
    ask_question(chat_id)

# ====== Quiz ======
def ask_question(chat_id):
    state = user_state[chat_id]
    qs = lessons[state["subject"]][state["chapter"]]
    if state["q_index"] >= len(qs):
        user_coins[chat_id] += 5
        bot.send_message(chat_id, f"Chapter finished! +5 coins. Total: {user_coins[chat_id]}")
        user_state.pop(chat_id)
        bot.send_message(chat_id, "Back to menu", reply_markup=main_menu())
        return
    bot.send_message(chat_id, f"Question: {qs[state['q_index']]['q']}")

def check_answer(chat_id, answer):
    state = user_state[chat_id]
    qs = lessons[state["subject"]][state["chapter"]]
    correct = qs[state["q_index"]]["a"].lower()
    if answer == correct:
        bot.send_message(chat_id, "Correct!")
        state["q_index"] += 1
        state["fail"] = 0
        ask_question(chat_id)
    else:
        state["fail"] += 1
        if state["fail"] >= 2:
            bot.send_message(chat_id, f"Failed twice. Skipping question.")
            state["q_index"] += 1
            state["fail"] = 0
            ask_question(chat_id)
        else:
            bot.send_message(chat_id, f"Wrong! Try again ({state['fail']}/2)")

# ====== Webhook routes ======
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is alive!", 200

@app.route("/leaderboard")
def leaderboard():
    sorted_users = sorted(user_coins.items(), key=lambda x: x[1], reverse=True)
    html = "<h2>Leaderboard</h2><ol>"
    for uid, coins in sorted_users:
        html += f"<li>User ID: {uid} - Coins: {coins}</li>"
    html += "</ol>"
    return render_template_string(html)

@app.before_first_request
def set_webhook():
    url = f"https://mahmudeducationbot.onrender.com/{TOKEN}"  # <-- YOUR Render URL
    bot.remove_webhook()
    bot.set_webhook(url=url)
    print("Webhook set:", url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
