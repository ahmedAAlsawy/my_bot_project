import telebot
import requests
import os
from flask import Flask, request

# جلب الإعدادات من خزنة Vercel
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)

def ask_ai(text):
    # قائمة بالاحتمالات التي تقبلها جوجل (سنجربها بالترتيب)
    endpoints = [
        {"ver": "v1beta", "mod": "gemini-1.5-flash"},
        {"ver": "v1", "mod": "gemini-1.5-flash"},
        {"ver": "v1beta", "mod": "gemini-pro"}
    ]
    
    last_error = ""
    for point in endpoints:
        url = f"https://generativelanguage.googleapis.com/{point['ver']}/models/{point['mod']}:generateContent?key={GEMINI_KEY}"
        payload = {"contents": [{"parts": [{"text": f"Correct this Arabic text and return ONLY the result: {text}"}]}]}
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            res_json = response.json()
            
            if response.status_code == 200:
                return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
            
            last_error = res_json.get('error', {}).get('message', 'Unknown error')
        except:
            continue
            
    return f"❌ لم نجد مساراً صالحاً.\nآخر رد من جوجل: {last_error}"

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200
    return "Bot is Active!", 200

# أمر جديد لفحص الموديلات المتاحة لمفتاحك "الآن وهو محمي"
@bot.message_handler(commands=['list'])
def list_models(message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
    try:
        res = requests.get(url).json()
        if 'models' in res:
            names = [m['name'] for m in res['models']]
            bot.reply_to(message, "✅ الموديلات المتاحة لمفتاحك هي:\n" + "\n".join(names))
        else:
            bot.reply_to(message, f"❌ فشل الفحص: {res}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ خطأ: {str(e)}")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    result = ask_ai(message.text)
    bot.reply_to(message, f"✨ النتيجة:\n\n{result}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True)
