import os, time, json, threading, requests
from flask import Flask
import telebot
from telebot import types

# ================= WEB SERVER FOR RENDER =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# ================= KEEP ALIVE =================
def keep_alive():
    while True:
        try:
            url = os.environ.get("RENDER_EXTERNAL_URL") or "https://mahmudeducationbot.onrender.com"
            requests.get(url, timeout=10)
        except:
            pass
        time.sleep(300)

threading.Thread(target=keep_alive, daemon=True).start()

# ================= BOT CONFIG =================
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise Exception("BOT TOKEN not set in environment variables!")

ADMIN_ID = 6648308251
OWNER_USERNAME = "@MHSM5"

FACEBOOK_LINK = "https://www.facebook.com/share/1DFvMtuJoU/"
TELEGRAM_LINK = "https://t.me/Mahmudsm1"
X_LINK = "https://x.com/Mahmud_sm1"
MY_USERNAME_LINK = "https://t.me/MHSM5"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================= STORAGE FILES =================
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "states": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(DB, f, ensure_ascii=False, indent=2)

DB = load_data()

def get_user(chat_id):
    chat_id = str(chat_id)
    if chat_id not in DB["users"]:
        DB["users"][chat_id] = {
            "coins": 0,
            "progress": {}
        }
        save_data()
    return DB["users"][chat_id]

def set_state(chat_id, state):
    DB["states"][str(chat_id)] = state
    save_data()

def get_state(chat_id):
    return DB["states"].get(str(chat_id))

def clear_state(chat_id):
    DB["states"].pop(str(chat_id), None)
    save_data()

# ================= MENUS =================
def main_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("🐍 Python")
    m.add("⚛ Physics")
    m.add("📐 Mathematics")
    m.add("🧪 Chemistry")
    m.add("💰 My Coins")
    m.add("🌐 My Links")
    m.add("ℹ️ About")
    return m

def links_menu():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("📘 Facebook", url=FACEBOOK_LINK))
    m.add(types.InlineKeyboardButton("📢 Telegram Channel", url=TELEGRAM_LINK))
    m.add(types.InlineKeyboardButton("🐦 X (Twitter)", url=X_LINK))
    m.add(types.InlineKeyboardButton("👤 My Username", url=MY_USERNAME_LINK))
    return m

# ================= LESSON DATA =================
# Each topic: lesson, example, q1, a1, q2, a2
LESSONS = {
    "python": [
        {"title":"What is Python",
         "lesson":"Python is a programming language used to build software.",
         "example":"print('Hello World')",
         "q1":"Python is a ____ ?","a1":"programming language",
         "q2":"Which function prints text?","a2":"print"},
        {"title":"Variables",
         "lesson":"Variables store data values.",
         "example":"x = 5",
         "q1":"x = 5 is a ____ ?","a1":"variable",
         "q2":"5 is of type? (int/str)","a2":"int"},
        {"title":"If Statement",
         "lesson":"If is used to make decisions.",
         "example":"if x > 0: print(x)",
         "q1":"If is used for?","a1":"decision",
         "q2":"Keyword for condition?","a2":"if"},
        {"title":"For Loop",
         "lesson":"For loop repeats code.",
         "example":"for i in range(3): print(i)",
         "q1":"For loop is for?","a1":"repeat",
         "q2":"Another loop is? (while/if)","a2":"while"},
    ],
    "physics": [
        {"title":"Speed",
         "lesson":"Speed is distance divided by time.",
         "example":"speed = distance / time",
         "q1":"Speed = distance / ____ ?","a1":"time",
         "q2":"Unit of speed?","a2":"m/s"},
        {"title":"Force",
         "lesson":"Force = mass x acceleration.",
         "example":"F = m * a",
         "q1":"Force = mass x ____ ?","a1":"acceleration",
         "q2":"Unit of force?","a2":"newton"},
    ],
    "math": [
        {"title":"Addition",
         "lesson":"Addition means adding numbers.",
         "example":"2 + 3 = 5",
         "q1":"10 + 5 = ?","a1":"15",
         "q2":"7 + 8 = ?","a2":"15"},
        {"title":"Multiplication",
         "lesson":"Multiplication means repeated addition.",
         "example":"5 x 3 = 15",
         "q1":"5 x 5 = ?","a1":"25",
         "q2":"9 x 3 = ?","a2":"27"},
    ],
    "chemistry": [
        {"title":"Atom",
         "lesson":"Atom is the smallest unit of matter.",
         "example":"Everything is made of atoms.",
         "q1":"Smallest unit of matter?","a1":"atom",
         "q2":"Center of atom?","a2":"nucleus"},
        {"title":"Elements",
         "lesson":"Elements are pure substances.",
         "example":"H is Hydrogen.",
         "q1":"H is symbol of?","a1":"hydrogen",
         "q2":"O is symbol of?","a2":"oxygen"},
    ],
}

# ================= HELPERS =================
def subject_menu(chat_id, subject):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i, t in enumerate(LESSONS[subject]):
        m.add(f"{i+1}. {t['title']}")
    m.add("⬅️ Back")
    set_state(chat_id, {"mode":"choose_topic","subject":subject})
    bot.send_message(chat_id, f"Select {subject.title()} topic:", reply_markup=m)

def start_topic(chat_id, subject, index):
    state = {
        "mode":"learning",
        "subject":subject,
        "index":index,
        "step":"lesson",  # lesson -> example -> q1 -> q2
        "fail":0
    }
    set_state(chat_id, state)
    show_current(chat_id)

def show_current(chat_id):
    state = get_state(chat_id)
    subject = state["subject"]
    idx = state["index"]
    topic = LESSONS[subject][idx]

    if state["step"] == "lesson":
        bot.send_message(chat_id, f"📘 <b>{topic['title']}</b>\n\n{topic['lesson']}\n\nSend <b>next</b> to continue.")
    elif state["step"] == "example":
        bot.send_message(chat_id, f"💡 Example:\n<code>{topic['example']}</code>\n\nSend <b>next</b>.")
    elif state["step"] == "q1":
        bot.send_message(chat_id, f"❓ Q1: {topic['q1']}")
    elif state["step"] == "q2":
        bot.send_message(chat_id, f"❓ Q2: {topic['q2']}")

def next_step(chat_id):
    state = get_state(chat_id)
    if not state: return
    if state["step"] == "lesson":
        state["step"] = "example"
    elif state["step"] == "example":
        state["step"] = "q1"
        state["fail"] = 0
    elif state["step"] == "q1":
        state["step"] = "q2"
        state["fail"] = 0
    elif state["step"] == "q2":
        # finish topic
        user = get_user(chat_id)
        user["coins"] += 5
        save_data()
        bot.send_message(chat_id, "✅ Topic finished! +5 coins.")
        # next topic or back
        subject = state["subject"]
        idx = state["index"] + 1
        if idx >= len(LESSONS[subject]):
            clear_state(chat_id)
            bot.send_message(chat_id, "🎉 Subject finished!", reply_markup=main_menu())
            return
        else:
            start_topic(chat_id, subject, idx)
            return
    set_state(chat_id, state)
    show_current(chat_id)

def check_answer(chat_id, text):
    state = get_state(chat_id)
    subject = state["subject"]
    idx = state["index"]
    topic = LESSONS[subject][idx]

    correct = topic["a1"].lower() if state["step"] == "q1" else topic["a2"].lower()

    if text.lower().strip() == correct:
        bot.send_message(chat_id, "✅ Correct!")
        next_step(chat_id)
    else:
        state["fail"] += 1
        if state["fail"] >= 2:
            bot.send_message(chat_id, "❌ Skipped this question.")
            next_step(chat_id)
        else:
            bot.send_message(chat_id, "❌ Wrong. Try again (1 more chance).")
        set_state(chat_id, state)

# ================= COMMANDS =================
@bot.message_handler(commands=["start"])
def start_cmd(msg):
    chat_id = msg.chat.id
    get_user(chat_id)
    bot.send_message(chat_id, "Welcome to Education Bot!", reply_markup=main_menu())

@bot.message_handler(commands=["broadcast"])
def broadcast_cmd(msg):
    chat_id = msg.chat.id
    if chat_id != ADMIN_ID:
        bot.reply_to(msg, "❌ You are not admin.")
        return
    text = msg.text.replace("/broadcast","").strip()
    if not text:
        bot.reply_to(msg, "Use: /broadcast message")
        return
    sent = 0
    for uid in DB["users"].keys():
        try:
            bot.send_message(int(uid), f"📢 Admin:\n\n{text}")
            sent += 1
        except:
            pass
    bot.send_message(chat_id, f"Sent to {sent} users.")

@bot.message_handler(commands=["users"])
def users_cmd(msg):
    if msg.chat.id != ADMIN_ID:
        return
    bot.send_message(msg.chat.id, f"Total users: {len(DB['users'])}")

# ================= MAIN HANDLER =================
@bot.message_handler(func=lambda m: True)
def handle(msg):
    chat_id = msg.chat.id
    text = msg.text.strip()

    get_user(chat_id)

    # Buttons
    if text == "💰 My Coins":
        u = get_user(chat_id)
        bot.send_message(chat_id, f"Your coins: {u['coins']}")
        return

    if text == "🌐 My Links":
        bot.send_message(chat_id, "My links:", reply_markup=links_menu())
        return

    if text == "ℹ️ About":
        bot.send_message(chat_id, f"This bot teaches Python, Physics, Mathematics, Chemistry.\nOwner: {OWNER_USERNAME}")
        return

    if text == "🐍 Python":
        subject_menu(chat_id, "python"); return
    if text == "⚛ Physics":
        subject_menu(chat_id, "physics"); return
    if text == "📐 Mathematics":
        subject_menu(chat_id, "math"); return
    if text == "🧪 Chemistry":
        subject_menu(chat_id, "chemistry"); return

    if text == "⬅️ Back":
        clear_state(chat_id)
        bot.send_message(chat_id, "Main menu", reply_markup=main_menu())
        return

    state = get_state(chat_id)
    if not state:
        return

    if state["mode"] == "choose_topic":
        subject = state["subject"]
        try:
            idx = int(text.split(".")[0]) - 1
            if 0 <= idx < len(LESSONS[subject]):
                start_topic(chat_id, subject, idx)
        except:
            bot.send_message(chat_id, "Please select from the buttons.")
        return

    if state["mode"] == "learning":
        if text.lower() == "next" and state["step"] in ["lesson","example"]:
            next_step(chat_id)
            return
        if state["step"] in ["q1","q2"]:
            check_answer(chat_id, text)
            return
        else:
            bot.send_message(chat_id, "Send 'next' to continue.")
            return

# ================= RUN =================
print("Bot is running...")
bot.infinity_polling(skip_pending=True)
