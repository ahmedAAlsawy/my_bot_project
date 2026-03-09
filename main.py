import telebot
import requests
from flask import Flask, request

# --- الإعدادات ---
TELEGRAM_TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
AI_KEY = 'AIzaSyDQbVmbXjy43DtWQsS6kc5FH9ICSZzc0Sg'

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)
user_data = {}

def ask_ai_api(text, lang):
    # مصفوفة المسارات المحتملة (سنختبرها واحداً تلو الآخر حتى ينجح أحدها)
    trials = [
        {"url": "v1beta", "model": "gemini-1.5-flash"},
        {"url": "v1", "model": "gemini-1.5-flash"},
        {"url": "v1beta", "model": "gemini-pro"}
    ]
    
    last_error = ""
    
    for trial in trials:
        api_version = trial["url"]
        model = trial["model"]
        endpoint = f"https://generativelanguage.googleapis.com/{api_version}/models/{model}:generateContent?key={AI_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": f"Correct this {lang} text: {text}"}]}]
        }
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            res_json = response.json()
            
            if response.status_code == 200 and 'candidates' in res_json:
                return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # إذا فشل المسار، نحفظ الخطأ وننتقل للتالي
            last_error = res_json.get('error', {}).get('message', 'Unknown error')
        except Exception as e:
            last_error = str(e)
            continue

    # إذا فشلت كل المحاولات، يظهر هذا الرد التفصيلي
    return f"❌ فشلت جميع المسارات.\nآخر خطأ: {last_error}\nنصيحة: تأكد من تفعيل (Generative Language API) في لوحة تحكم جوجل."

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200
    return "Bot is Active!", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 نظام التدقيق المرن يعمل الآن. أرسل نصك وسأحاول معالجته بأكثر من مسار.")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    # تحديد اللغة تلقائياً كـ Arabic مؤقتاً للتجربة
    result = ask_ai_api(message.text, "Arabic")
    bot.reply_to(message, f"✨ النتيجة:\n\n{result}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True)
