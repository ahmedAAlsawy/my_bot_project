import telebot
from flask import Flask, request

TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# ذاكرة مؤقتة
user_data = {}

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "<h1>البوت يعمل بنظام اللغات!</h1>", 200

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    user_data[uid] = {'lang': 'ar', 'count': 0}
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('العربية 🇪🇬', 'English 🇺🇸')
    bot.reply_to(message, "أهلاً بك يا أحمد! اختر لغة التدقيق الآن من القائمة بالأسفل:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['العربية 🇪🇬', 'English 🇺🇸'])
def set_lang(message):
    uid = message.from_user.id
    lang = 'ar' if 'العربية' in message.text else 'en'
    if uid not in user_data: user_data[uid] = {'count': 0}
    user_data[uid]['lang'] = lang
    bot.reply_to(message, f"تم تفعيل اللغة: {message.text}. ابدأ بإرسال النصوص.")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    if uid not in user_data: user_data[uid] = {'lang': 'ar', 'count': 0}
    
    # عداد الكلمات
    words = len(message.text.split())
    user_data[uid]['count'] += words
    
    if user_data[uid]['count'] > 20:
        bot.reply_to(message, "⚠️ انتهت الكلمات المجانية (20 كلمة). للاشتراك تواصل مع المطور: @Ahmed_Aalsawy")
        return

    # تصحيح بسيط كمثال
    text = message.text
    if user_data[uid]['lang'] == 'ar':
        text = text.replace("لاكن", "لكن").replace("احمد", "أحمد")
    else:
        text = text.replace("teh", "the")

    bot.reply_to(message, f"✅ التصحيح:\n{text}\n\n📊 استهلكت {user_data[uid]['count']}/20 كلمة.")

# هذا الجزء ضروري جداً لـ Vercel
def handler(event, context):
    return app(event, context)
