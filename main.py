import os
import threading
from flask import Flask
import telebot
from telebot import types

# ================== CONFIG ==================
TOKEN = os.environ.get("BOT_TOKEN", "SAKA_TOKEN_DINKA_ANAN")

bot = telebot.TeleBot(TOKEN, threaded=True)

# ================== FLASK (KEEP ALIVE) ==================
app = Flask(__name__)

@app.route("/")
def home():
    return "MahmudEducationBot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================== MENU FUNCTIONS ==================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📚 Lessons")
    btn2 = types.KeyboardButton("💰 Coins")
    btn3 = types.KeyboardButton("🏆 Leaderboard")
    btn4 = types.KeyboardButton("👤 Profile")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

# ================== BOT HANDLERS ==================
@bot.message_handler(commands=["start"])
def start(message):
    name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"👋 Sannu {name}!\n\nBarka da zuwa *Mahmud Education Bot* 📚\nZaɓi abu daga menu a ƙasa:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "📚 Lessons")
def lessons(message):
    bot.send_message(message.chat.id, "📚 *Lessons* zasu zo nan ba da daɗewa ba 😉", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 Coins")
def coins(message):
    bot.send_message(message.chat.id, "💰 Kana da *0 coins* yanzu.\n(Soon system zai fara aiki)", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏆 Leaderboard")
def leaderboard(message):
    bot.send_message(message.chat.id, "🏆 *Leaderboard* zai zo nan gaba insha Allah.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):
    user = message.from_user
    text = f"👤 *Profile ɗinka:*\n\n" \
           f"👨 Suna: {user.first_name}\n" \
           f"🆔 ID: `{user.id}`\n" \
           f"💰 Coins: 0"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ================== START BOT ==================
def run_bot():
    # Tabbatar webhook baya aiki
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
