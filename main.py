import telebot
import requests
from flask import Flask, request

# --- الإعدادات ---
TELEGRAM_TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
AI_KEY = 'AIzaSyDQbVmbXjy43DtWQsS6kc5FH9ICSZzc0Sg'

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)

# دالة لجلب الموديلات المتاحة فعلياً لحسابك
def get_available_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={AI_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'models' in data:
            # سنستخرج الأسماء فقط لنعرضها لك
            return "\n".join([m['name'] for m in data['models']])
        return f"❌ لم نجد موديلات. الرد: {data}"
    except Exception as e:
        return f"⚠️ خطأ في الجلب: {str(e)}"

def ask_ai(text):
    # سنحاول استخدام هذا الاسم الافتراضي
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_KEY}"
    payload = {"contents": [{"parts": [{"text": text}]}]}
    try:
        response = requests.post(url, json=payload, timeout=15)
        res_json = response.json()
        if response.status_code == 200:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        return f"❌ خطأ {response.status_code}: {res_json.get('error', {}).get('message', 'Unknown')}"
    except Exception as e:
        return f"⚠️ خطأ اتصال: {str(e)}"

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200
    return "Bot is Active!", 200

@bot.message_handler(commands=['list'])
def list_models_command(message):
    bot.reply_to(message, "🔍 جاري فحص الموديلات المتاحة في حسابك...")
    models = get_available_models()
    bot.reply_to(message, f"📋 الموديلات المتاحة لك هي:\n\n{models}")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    result = ask_ai(message.text)
    bot.reply_to(message, f"✨ النتيجة:\n\n{result}\n\n💡 أرسل /list لمعرفة الموديلات المتاحة.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True)
