import telebot
from flask import Flask, request

TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# قاعدة بيانات مؤقتة (سيتم تصفيرها عند ريستارت السيرفر - للأفضل استخدم قاعدة بيانات لاحقاً)
user_data = {}

# قاموس اللغات والتصحيحات
LANGS = {
    'ar': {'name': 'العربية', 'msg': 'تم اختيار العربية', 'fix': {'لاكن': 'لكن', 'احمد': 'أحمد'}},
    'en': {'name': 'English', 'msg': 'English selected', 'fix': {'teh': 'the', 'i ': 'I '}}
}

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200
    return "Bot is Running", 200

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    user_data[uid] = {'lang': 'ar', 'count': 0}
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('العربية 🇪🇬', 'English 🇺🇸')
    bot.reply_to(message, "أهلاً بك! اختر لغة التدقيق:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['العربية 🇪🇬', 'English 🇺🇸'])
def set_lang(message):
    uid = message.from_user.id
    lang_code = 'ar' if 'العربية' in message.text else 'en'
    if uid not in user_data: user_data[uid] = {'count': 0}
    user_data[uid]['lang'] = lang_code
    bot.reply_to(message, LANGS[lang_code]['msg'])

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    uid = message.from_user.id
    if uid not in user_data: user_data[uid] = {'lang': 'ar', 'count': 0}
    
    # نظام العداد (الحد الأقصى 20 كلمة مثلاً)
    words_count = len(message.text.split())
    user_data[uid]['count'] += words_count
    
    if user_data[uid]['count'] > 20:
        bot.reply_to(message, "⚠️ انتهت الفترة المجانية. يرجى الدفع للاستمرار.\nللتواصل مع المطور: @Ahmed_Aalsawy")
        return

    # منطق التصحيح حسب اللغة المختارة
    lang = user_data[uid]['lang']
    text = message.text
    corrections = LANGS[lang]['fix']
    
    fixed_text = text
    for wrong, right in corrections.items():
        fixed_text = fixed_text.replace(wrong, right)
    
    if fixed_text != text:
        bot.reply_to(message, f"✅ التصحيح ({LANGS[lang]['name']}):\n{fixed_text}\n\n📊 استهلكت {user_data[uid]['count']}/20 كلمة.")
    else:
        bot.reply_to(message, f"نصك سليم! استهلكت {user_data[uid]['count']}/20 كلمة.")

def handler(event, context):
    return app(event, context)
