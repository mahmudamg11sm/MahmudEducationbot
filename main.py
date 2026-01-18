import os
import telebot
from flask import Flask
from threading import Thread
from telebot import types

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN or ":" not in TOKEN:
    raise Exception("BOT_TOKEN not set correctly")

bot = telebot.TeleBot(TOKEN, threaded=True)

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return "MahmudEducationBot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================= MENUS =================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📚 Lessons", "💰 Coins")
    markup.add("🏆 Leaderboard", "👤 Profile")
    return markup

def lessons_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🐍 Python", "🧮 Math")
    markup.add("🔙 Back")
    return markup

# ================= HANDLERS =================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Barka da zuwa *Mahmud Education Bot*\n\nZaɓi abu daga menu:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "📚 Lessons")
def lessons(message):
    bot.send_message(
        message.chat.id,
        "📚 Zaɓi subject:",
        reply_markup=lessons_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🔙 Back")
def back(message):
    bot.send_message(message.chat.id, "⬅️ Komawa menu:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🐍 Python")
def python_lessons(message):
    bot.send_message(message.chat.id, "🐍 Python lessons zasu zo nan ba da daɗewa ba 😉")

@bot.message_handler(func=lambda m: m.text == "🧮 Math")
def math_lessons(message):
    bot.send_message(message.chat.id, "🧮 Math lessons zasu zo nan ba da daɗewa ba 😉")

@bot.message_handler(func=lambda m: m.text == "💰 Coins")
def coins(message):
    bot.send_message(message.chat.id, "💰 Kana da 0 coins yanzu.")

@bot.message_handler(func=lambda m: m.text == "🏆 Leaderboard")
def leaderboard(message):
    bot.send_message(message.chat.id, "🏆 Leaderboard zai zo nan gaba.")

@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):
    user = message.from_user
    bot.send_message(
        message.chat.id,
        f"👤 Profile ɗinka:\n\n"
        f"👨 Suna: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"💰 Coins: 0"
    )

# ================= RUN =================
def run_bot():
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()
