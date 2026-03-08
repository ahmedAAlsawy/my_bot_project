from flask import Flask, request
import telebot

# توكن بوتك الخاص
TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# إعداد أوامر البوت لتظهر للمستخدم
bot.set_my_commands([
    telebot.types.BotCommand("/start", "تشغيل البوت"),
    telebot.types.BotCommand("/help", "قواعد التدقيق")
])

@app.route('/', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    # رسالة تظهر عند فتح الرابط في المتصفح للتأكد أن السيرفر يعمل
    return "<h1>البوت يعمل بنجاح! 🚀</h1>", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك يا أحمد! أنا الآن أعمل من سيرفر Vercel 24 ساعة.")

@bot.message_handler(func=lambda message: True)
def auto_correct(message):
    text = message.text
    # قواعد تصحيح بسيطة
    if "لاكن" in text:
        bot.reply_to(message, "💡 تصحيح لغوي: اكتبها 'لكن' (بدون ألف).")
    elif "احمد" in text:
        bot.reply_to(message, "💡 تصحيح لغوي: اكتب 'أحمد' بالهمزة.")
    else:
        bot.reply_to(message, f"وصلتني رسالتك: {text}")

# أهم جزء لتشغيل Flask على Vercel
def handler(event, context):
    return app(event, context)
