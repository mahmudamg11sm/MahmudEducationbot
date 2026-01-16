import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import time

# ================== CONFIG ==================
TOKEN = "TOKEN"
ADMIN_ID = 6648308251

OWNER_USERNAME = "@MHSM5"

FACEBOOK_LINK = "https://www.facebook.com/share/1DFvMtuJoU/"
TELEGRAM_LINK = "https://t.me/Mahmudsm1"
X_LINK = "https://x.com/Mahmud_sm1"
MY_USERNAME_LINK = "https://t.me/MHSM5"
# ===========================================

bot = telepot.Bot(TOKEN)

all_users = set()
user_state = {}
user_coins = {}

# ================== KEYBOARDS ==================
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

# ================== HANDLER ==================
def handle(msg):
    chat_id = msg['chat']['id']
    text = str(msg.get('text', '')).strip()

    all_users.add(chat_id)

    if chat_id not in user_coins:
        user_coins[chat_id] = 0

    text_low = text.lower()

    # ========== ADMIN BROADCAST ==========
    if chat_id == ADMIN_ID and text_low.startswith("/broadcast"):
        msg_text = text.replace("/broadcast", "").strip()
        if not msg_text:
            bot.sendMessage(chat_id, "Use: /broadcast Your message")
            return

        sent = 0
        for user in all_users:
            try:
                bot.sendMessage(user, f"Admin:\n{msg_text}")
                sent += 1
            except:
                pass

        bot.sendMessage(chat_id, f"Sent to {sent} users.")
        return

    # ========== START ==========
    if text_low == "/start":
        bot.sendMessage(chat_id, "Welcome to Education Bot!", reply_markup=main_menu())
        return

    # ========== MY COINS ==========
    if text == "💰 My Coins":
        bot.sendMessage(chat_id, f"Your coins: {user_coins[chat_id]}")
        return

    # ========== ABOUT ==========
    if text == "ℹ️ About":
        bot.sendMessage(chat_id,
        "This bot helps people learn:\n"
        "Python, Physics, Mathematics, Chemistry.\n\n"
        f"Owner: {OWNER_USERNAME}")
        return

    # ========== LINKS ==========
    if text == "🌐 My Links":
        bot.sendMessage(chat_id, "Follow me here:", reply_markup=links_menu())
        return

    # ========== SUBJECT SELECT ==========
    if text == "🐍 Python Lessons":
        show_chapters(chat_id, "python")
        return

    if text == "⚛ Physics Lessons":
        show_chapters(chat_id, "physics")
        return

    if text == "📐 Mathematics Lessons":
        show_chapters(chat_id, "math")
        return

    if text == "🧪 Chemistry Lessons":
        show_chapters(chat_id, "chemistry")
        return

    # ========== CHAPTER SELECT ==========
    if chat_id in user_state and user_state[chat_id]["mode"] == "select_chapter":
        select_chapter(chat_id, text)
        return

    # ========== ANSWERING ==========
    if chat_id in user_state and user_state[chat_id]["mode"] == "quiz":
        check_answer(chat_id, text_low)
        return

# ================== CHAPTER SYSTEM ==================
def show_chapters(chat_id, subject):
    chapters = lessons[subject].keys()
    keyboard = []

    for ch in chapters:
        keyboard.append([KeyboardButton(text=ch.title())])

    keyboard.append([KeyboardButton(text="⬅️ Back to Menu")])

    user_state[chat_id] = {
        "mode": "select_chapter",
        "subject": subject
    }

    bot.sendMessage(
        chat_id,
        f"Select {subject.title()} Chapter:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

def select_chapter(chat_id, text):
    if text == "⬅️ Back to Menu":
        if chat_id in user_state:
            del user_state[chat_id]
        bot.sendMessage(chat_id, "Main Menu", reply_markup=main_menu())
        return

    state = user_state[chat_id]
    subject = state["subject"]
    key = text.lower()

    if key not in lessons[subject]:
        bot.sendMessage(chat_id, "Please select from the buttons.")
        return

    user_state[chat_id] = {
        "mode": "quiz",
        "subject": subject,
        "chapter": key,
        "q_index": 0,
        "fail": 0
    }

    ask_question(chat_id)

# ================== QUIZ ==================
def ask_question(chat_id):
    state = user_state[chat_id]
    subject = state["subject"]
    chapter = state["chapter"]

    qs = lessons[subject][chapter]

    if state["q_index"] >= len(qs):
        user_coins[chat_id] += 5
        bot.sendMessage(chat_id, f"Chapter finished! +5 coins. Total: {user_coins[chat_id]}")
        del user_state[chat_id]
        bot.sendMessage(chat_id, "Back to menu", reply_markup=main_menu())
        return

    q = qs[state["q_index"]]["q"]
    bot.sendMessage(chat_id, f"Question: {q}")

def check_answer(chat_id, answer):
    state = user_state[chat_id]
    subject = state["subject"]
    chapter = state["chapter"]

    qs = lessons[subject][chapter]
    correct = qs[state["q_index"]]["a"].lower()

    if answer == correct:
        bot.sendMessage(chat_id, "Correct!")
        state["q_index"] += 1
        state["fail"] = 0
        ask_question(chat_id)
    else:
        state["fail"] += 1
        if state["fail"] >= 3:
            bot.sendMessage(chat_id, "Failed this question. Skipping...")
            state["q_index"] += 1
            state["fail"] = 0
            ask_question(chat_id)
        else:
            bot.sendMessage(chat_id, f"Wrong! Try again ({state['fail']}/3)")

# ================== RUN ==================
MessageLoop(bot, handle).run_as_thread()
print("Education Bot is running...")

while True:
    time.sleep(10)
