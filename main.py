import os
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN or ":" not in TOKEN:
    raise Exception("❌ BOT_TOKEN ba a saka shi daidai a Render Environment Variables ba!")

bot = telebot.TeleBot(TOKEN, threaded=True)

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================= MENU / BUTTONS =================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📚 Lessons", "ℹ️ Info")
    markup.row("🔗 Links")
    return markup

@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(
        message.chat.id,
        f"Assalamu alaikum {message.from_user.first_name}!\nZaɓi daga menu:",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text
    if text == "📚 Lessons":
        bot.send_message(message.chat.id, "Ga darussan da zaku iya koya...")
    elif text == "ℹ️ Info":
        bot.send_message(message.chat.id, "Wannan bot na koyar da ilimi ne.")
    elif text == "🔗 Links":
        bot.send_message(
            message.chat.id,
            "Telegram: https://t.me/Mahmudsm1\n"
            "X / Twitter: https://x.com/Mahmud_sm1\n"
            "Facebook: https://www.facebook.com/share/19iY36vXk9/"
        )
    else:
        bot.send_message(message.chat.id, "Babu wannan zaɓi a menu!", reply_markup=main_menu())

# ================= RUN BOT =================
if __name__ == "__main__":
    # Cire duk previous webhooks da tsaftace polling
    bot.remove_webhook()
    # Start Flask keep-alive
    Thread(target=run_flask).start()
    # Start Telegram bot polling mai safe
    bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
