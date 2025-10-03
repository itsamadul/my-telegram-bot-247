from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import os

TOKEN = os.getenv("BOT_TOKEN")

# Create Flask app
app = Flask(__name__)

# Telegram bot application
bot_app = Application.builder().token(TOKEN).build()

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Bot is alive on Vercel!")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📖 Commands:\n/start - Start bot\n/help - Show help")

# Add handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("help", help))

# Flask route for webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put_nowait(update)
    return "ok", 200

@app.route("/")
def home():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(port=5000)
