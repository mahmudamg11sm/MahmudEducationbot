import telebot
from telebot import types
from flask import Flask
from threading import Thread
import json, os

# ================== CONFIG ==================
TOKEN = os.environ.get("TOKEN")  # Bot Token from Telegram
ADMIN_ID = int(os.environ.get("ADMIN_ID", 6648308251))  # Only admin can broadcast or check leaderboard
OWNER_USERNAME = "@MHSM5"

# Coin reward per topic
COINS_PER_TOPIC = int(os.environ.get("COINS_PER_TOPIC", 5))

# ================== BOT & FLASK ==================
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_flask).start()

# ================== DATABASE ==================
DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE,"r") as f:
        return json.load(f)

def save_db():
    with open(DB_FILE,"w") as f:
        json.dump(db,f,indent=2)

db = load_db()

def get_user(uid):
    uid = str(uid)
    if uid not in db:
        db[uid] = {
            "coins":0,
            "progress":{"python":0,"physics":0,"math":0,"chemistry":0}
        }
        save_db()
    return db[uid]

# ================== USER STATE ==================
state = {}

# ================== LESSONS ==================
# Example lessons, you can expand
courses = {
    "python":[
        {"title":"Variables","lesson":"Variables store data values.","example":"x = 5","q":[{"q":"What stores data values?","a":"variables"},{"q":"x=5, x is a?","a":"variable"}]},
        {"title":"If Statement","lesson":"If statements make decisions.","example":"if x>5:","q":[{"q":"If is used for?","a":"decision"},{"q":"If checks a?","a":"condition"}]}
    ],
    "physics":[
        {"title":"Speed","lesson":"Speed = distance/time","example":"v = d/t","q":[{"q":"Speed = distance/?","a":"time"},{"q":"Unit of speed?","a":"m/s"}]}
    ],
    "math":[
        {"title":"Addition","lesson":"Addition means plus.","example":"2+3=5","q":[{"q":"2+2=?","a":"4"},{"q":"5+5=?","a":"10"}]}
    ],
    "chemistry":[
        {"title":"Atom","lesson":"Atom is smallest unit of matter.","example":"Everything is made of atoms","q":[{"q":"Smallest unit of matter?","a":"atom"},{"q":"Everything is made of?","a":"atoms"}]}
    ]
}

# ================== MENUS ==================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🐍 Python","⚛ Physics")
    markup.row("📐 Math","🧪 Chemistry")
    markup.row("💰 My Coins","ℹ️ About")
    return markup

def topic_markup(subject,index):
    markup = types.InlineKeyboardMarkup()
    for i,t in enumerate(courses[subject]):
        done = "✅" if i<index else ""
        markup.add(types.InlineKeyboardButton(text=f"{t['title']} {done}",callback_data=f"topic_{subject}_{i}"))
    return markup

def next_topic_button(subject):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Next Topic",callback_data=f"next_{subject}"))
    return markup

# ================== HANDLERS ==================
@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.chat.id
    get_user(uid)
    bot.send_message(uid,"Welcome to Education Bot!", reply_markup=main_menu())

@bot.message_handler(commands=["users"])
def users_cmd(msg):
    if msg.chat.id != ADMIN_ID: return
    sorted_users = sorted(db.items(), key=lambda x:x[1]["coins"], reverse=True)
    text = "Leaderboard:\n"
    for i,(uid,u) in enumerate(sorted_users):
        text += f"{i+1}. {uid}: {u['coins']} coins\n"
    bot.send_message(msg.chat.id,text)

@bot.message_handler(commands=["broadcast"])
def broadcast(msg):
    if msg.chat.id != ADMIN_ID: return
    text = msg.text.replace("/broadcast","").strip()
    for u in db:
        try: bot.send_message(int(u),f"Admin:\n{text}")
        except: pass
    bot.send_message(msg.chat.id,"Broadcast sent!")

@bot.message_handler(func=lambda m: True)
def handler(msg):
    uid = msg.chat.id
    text = msg.text.lower()
    user = get_user(uid)

    if text == "💰 my coins":
        bot.send_message(uid,f"Your coins: {user['coins']}")
        return
    if text == "ℹ️ about":
        bot.send_message(uid,f"Bot helps learn Python, Physics, Math, Chemistry.\nOwner: {OWNER_USERNAME}")
        return

    subjects = {"🐍 python":"python","⚛ physics":"physics","📐 math":"math","🧪 chemistry":"chemistry"}
    if text in subjects:
        s = subjects[text]
        user_progress = user["progress"][s]
        bot.send_message(uid,f"Select Topic for {s.title()}:",reply_markup=topic_markup(s,user_progress))
        return

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.message.chat.id
    data = call.data
    user = get_user(uid)

    if data.startswith("topic_"):
        _,subject,index = data.split("_")
        index = int(index)
        state[uid] = {"subject":subject,"topic_index":index,"q_index":-1,"fails":0}
        topic = courses[subject][index]
        bot.send_message(uid,f"📘 {topic['title']}\n{topic['lesson']}\nExample:\n{topic['example']}\n\nPress Next Topic to continue",reply_markup=next_topic_button(subject))

    elif data.startswith("next_"):
        subject = data.split("_")[1]
        idx = state[uid]["topic_index"]+1 if uid in state else user["progress"][subject]
        if idx >= len(courses[subject]):
            bot.send_message(uid,"✅ You finished this subject!", reply_markup=main_menu())
        else:
            user["progress"][subject] = idx
            user["coins"] += COINS_PER_TOPIC
            save_db()
            bot.send_message(uid,f"Select next topic for {subject.title()}:", reply_markup=topic_markup(subject,idx))
            if uid in state: del state[uid]

# ================== RUN ==================
print("Education Bot 3.0 running...")
bot.infinity_polling()
