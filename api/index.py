from flask import Flask, request
import telebot

# التوكن الخاص بك مدمج هنا
TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# دالة استقبال الرسائل من تليجرام (الجرس)
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

# أمر البداية /start
@bot.message_handler(commands=['start'])
def start(message):
    welcome_msg = (
        "أهلاً بك يا أحمد في بوت التدقيق اللغوي! 🖋️\n\n"
        "أنا أعمل الآن بنظام الـ Webhooks المستقر على Vercel.\n"
        "أرسل لي أي جملة وسأحاول مساعدتك."
    )
    bot.reply_to(message, welcome_msg)

# ميزة تجريبية: تصحيح أخطاء شائعة (مثال)
@bot.message_handler(func=lambda message: True)
def auto_correct(message):
    text = message.text
    corrections = {
        "لاكن": "لكن",
        "احمد": "أحمد",
        "انشاء الله": "إن شاء الله",
        "انت": "أنتِ / أنتَ"
    }
    
    response = text
    changed = False
    for wrong, right in corrections.items():
        if wrong in text:
            response = response.replace(wrong, f"*{right}*")
            changed = True
            
    if changed:
        bot.reply_to(message, f"تنبيه لغوي: هل تقصد:\n{response}")
    else:
        bot.reply_to(message, "جملتك سليمة أو لم أجد فيها خطأً شائعاً حالياً.")

# هذه الجزئية ضرورية لـ Vercel
def handler(event, context):
    return app(event, context)
