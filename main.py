import telebot
import requests
import os
from flask import Flask, request

# --- جلب الإعدادات من الخزنة (Environment Variables) ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
MODEL_NAME = "gemini-1.5-flash-latest"

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)

def ask_ai(text):
    # استخدام المسار المستقر v1
    url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"Correct this Arabic text: {text}"}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        res_json = response.json()
        
        if response.status_code == 200:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # كاشف أخطاء متطور
        error_msg = res_json.get('error', {}).get('message', 'خطأ غير معروف')
        return f"❌ خطأ {response.status_code}: {error_msg}"
    except Exception as e:
        return f"⚠️ خطأ اتصال: {str(e)}"

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200
    return "Bot is Active!", 200

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    result = ask_ai(message.text)
    bot.reply_to(message, f"✨ النتيجة:\n\n{result}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True)
