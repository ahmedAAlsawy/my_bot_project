from flask import Flask, request
import telebot

TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# 1. قائمة الأوامر (تظهر للمستخدم بجانب خانة الكتابة)
bot.set_my_commands([
    telebot.types.BotCommand("/start", "بداية التشغيل"),
    telebot.types.BotCommand("/help", "المساعدة والقواعد")
])

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
    return 'Bot is Running', 200

# 2. ماذا يحدث عند الضغط على /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("تواصل مع المطور", url="https://t.me/ahmedAAlsawy")
    markup.add(btn)
    bot.reply_to(message, "مرحباً بك يا أحمد! بوت التدقيق جاهز للخدمة.", reply_markup=markup)

# 3. الرد على أي نص (التدقيق اللغوي)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text
    if "لاكن" in text:
        bot.reply_to(message, "💡 تصحيح: 'لكن' (بدون ألف).")
    else:
        bot.reply_to(message, "وصلتني رسالتك وسأدققها.")

def handler(event, context):
    return app(event, context)
