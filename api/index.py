from flask import Flask, request
import telebot

TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
# مهم جداً وضع threaded=False في بيئات الـ Serverless مثل Vercel
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        try:
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
        except Exception as e:
            print(f"Error: {e}")
        return "OK", 200
    return "<h1>البوت يعمل! أرسل رسالة في تليجرام.</h1>", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أهلاً يا أحمد! تم الإصلاح والبوت يعمل الآن 🚀")

@bot.message_handler(func=lambda message: True)
def correct(message):
    text = message.text
    if "لاكن" in text:
        bot.reply_to(message, "💡 تصحيح: اكتبها 'لكن'.")
    else:
        bot.reply_to(message, f"وصلتني رسالتك: {text}")

# هذا السطر هو الأهم لتشغيل المشروع على Vercel
def handler(event, context):
    return app(event, context)
