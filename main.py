import telebot
import requests
import os
from flask import Flask, request

# جلب الإعدادات من خزنة Vercel
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
# اخترنا الموديل الذي أكد حسابك وجوده في القائمة
MODEL_NAME = "gemini-2.0-flash"

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)

def ask_ai(text):
    # استخدام المسار v1beta لأنه الأكثر توافقاً مع الموديلات الحديثة في قائمتك
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Correct all spelling and grammar errors in this Arabic text and return ONLY the corrected text: {text}"}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        res_json = response.json()
        
        if response.status_code == 200:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return f"❌ خطأ تقني: {res_json.get('error', {}).get('message', 'يرجى المحاولة لاحقاً')}"
    except Exception as e:
        return f"⚠️ خطأ اتصال: {str(e)}"

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200
    return "البوت يعمل بكفاءة!", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✨ أهلاً بك في بوت التدقيق اللغوي الذكي (إصدار Gemini 2.0).\n\nأرسل أي نص الآن وسأقوم بتصحيحه فوراً!")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    result = ask_ai(message.text)
    bot.reply_to(message, f"✨ النتيجة:\n\n{result}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True)
