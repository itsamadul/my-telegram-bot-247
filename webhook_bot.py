# -*- coding: utf-8 -*-
import os
import json
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
# Gemini API ব্যবহারের জন্য (ভবিষ্যতে ইন্টিগ্রেট করা হবে)
# from google import genai 

# --- কনফিগারেশন এবং সেটআপ ---
# এই ভেরিয়েবলগুলো আপনার হোস্টিং প্ল্যাটফর্মে সেট করতে হবে।
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

app = Flask(__name__)

# টেলিগ্রাম বট এবং ডিসপ্যাচার ইনিশিয়ালাইজ করা
try:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set.")
    bot = Bot(token=BOT_TOKEN)
    # workers=0 মানে এটি শুধুমাত্র Webhook-এর মাধ্যমে কাজ করবে, যা 24/7 ফ্রি হোস্টিংয়ের জন্য জরুরি।
    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
    print("Bot and Dispatcher initialized successfully.")
except Exception as e:
    print(f"Error initializing bot: {e}")
    bot = None
    dispatcher = None


# --- ১. কমান্ড হ্যান্ডলার ফাংশন ---

def start_command(update, context):
    """/start কমান্ড হ্যান্ডেল করে।"""
    user_name = update.effective_user.first_name or "বন্ধু"
    response_text = (
        f"হ্যালো {user_name}! 👋 আমি আপনার মাল্টি-ফাংশনাল বট।\n\n"
        "আমার সব কাজ দেখতে /help টাইপ করুন, অথবা মেনু দেখতে /menu টাইপ করুন।"
    )
    update.message.reply_text(response_text)

def help_command(update, context):
    """/help কমান্ড হ্যান্ডেল করে।"""
    response_text = (
        "এখানে আমার উপলব্ধ কমান্ডগুলো রয়েছে:\n"
        "/start - বট শুরু করুন\n"
        "/help - এই সাহায্য বার্তাটি দেখান\n"
        "/menu - প্রধান ফিচার মেনু দেখুন\n"
        "/ai_chat - AI এর সাথে চ্যাট শুরু করুন (এখনো AI লজিক যুক্ত হয়নি)\n"
        "/image - ছবি তৈরি করুন (ভবিষ্যতে)\n"
    )
    update.message.reply_text(response_text)

def menu_command(update, context):
    """/menu কমান্ড হ্যান্ডেল করে।"""
    response_text = (
        "🌟 **প্রধান মেনু** 🌟\n\n"
        "আপনি কোন কাজটি করতে চান, অনুগ্রহ করে একটি বিকল্প বেছে নিন:\n"
        "1.  `/ai_chat`: যেকোনো প্রশ্ন করুন বা গল্প লিখুন।\n"
        "2.  `/image`: AI দ্বারা ছবি তৈরি করুন।\n"
        "3.  `/down`: ফাইল ডাউনলোডের বিকল্প (যদি থাকে)।\n"
        "4.  `/help`: সব কমান্ডের তালিকা।\n"
    )
    update.message.reply_text(response_text)

def ai_chat_command(update, context):
    """/ai_chat কমান্ডের জন্য প্রাথমিক বার্তা।"""
    response_text = (
        "🤖 **AI চ্যাট মোড শুরু হলো!**\n\n"
        "এখন আপনি আমাকে যা খুশি জিজ্ঞাসা করতে পারেন। আপনার AI লজিক এখনও যুক্ত করা হয়নি।"
    )
    update.message.reply_text(response_text)

def echo_message(update, context):
    """যে কোনো মেসেজ পেলে তা রিপিট করে। এটি শুধু পরীক্ষার জন্য।"""
    text = update.message.text
    update.message.reply_text(f"আপনি বললেন: {text}")


# --- ২. ডিসপ্যাচার সেটআপ ---
if dispatcher:
    # কমান্ড হ্যান্ডলার
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("menu", menu_command))
    dispatcher.add_handler(CommandHandler("ai_chat", ai_chat_command))
    
    # মেসেজ হ্যান্ডলার (কমান্ড ছাড়া বাকি টেক্সট মেসেজ)
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))


# --- ৩. Flask Webhook রুট ---

@app.route('/', methods=['GET'])
def home():
    """হোম রুট (স্বাস্থ্য পরীক্ষা)"""
    return jsonify({"status": "Bot is operational in Webhook mode"}), 200

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    """টেলিগ্রাম থেকে আসা সমস্ত Webhook আপডেট গ্রহণ করার রুট।"""
    if not BOT_TOKEN:
        print("Webhook called, but BOT_TOKEN is missing.")
        return jsonify({"message": "Configuration error"}), 500

    if request.method == "POST":
        try:
            json_data = request.get_json(force=True)
            update = Update.de_json(json_data, bot)
            if dispatcher:
                dispatcher.process_update(update)
            return jsonify({"status": "ok"}), 200

        except Exception as e:
            # টেলিগ্রামকে 200 OK পাঠাতে হবে, না হলে সে বারবার একই মেসেজ পাঠাবে।
            print(f"Error processing update: {e}")
            return jsonify({"status": "error", "message": str(e)}), 200
    
    return jsonify({"status": "not allowed"}), 405
