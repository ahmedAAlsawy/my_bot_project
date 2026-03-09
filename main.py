import telebot
import requests
from flask import Flask, request

# --- الإعدادات ---
TELEGRAM_TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
# المفتاح الجديد الذي أرسلته
AI_KEY = 'AIzaSyDQbVmbXjy43DtWQsS6kc5FH9ICSZzc0Sg'
MODEL_NAME = "gemini-1.5-flash"

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)
user_data = {}

LANG_CONFIG = {
    'العربية 🇪🇬': {'name': 'Arabic', 'msg': '✅ تم تفعيل التدقيق بالعربية.'},
    'English 🇺🇸': {'name': 'English', 'msg': '✅ English enabled.'},
    'Русский 🇷🇺': {'name': 'Russian', 'msg': '✅ Проверка включена.'},
    '中文 🇨🇳': {'name': 'Chinese', 'msg': '✅ 中文校对已启用.'},
    'עברית 🇮🇱': {'name': 'Hebrew', 'msg': '✅ בדיקת עברית הופעלה.'},
    'فارسی 🇮🇷': {'name': 'Persian', 'msg': '✅ ویرایش فارسی فعال شد.'},
    'Français 🇫🇷': {'name': 'French', 'msg': '✅ Correction française activée.'}
}

def ask_ai_api(text, lang):
    # عدنا للرابط القياسي الذي سيعمل فوراً مع المفتاح الجديد
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={AI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Correct all errors in the following {lang} text and return ONLY the result: {text}"}]
        }]
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        res_json = response.json()
        
        if response.status_code == 200 and 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        
        error_info = res_json.get('error', {})
        return f"❌ خطأ ({response.status_code}): {error_info.get('message', 'خطأ غير معروف')}"

    except Exception as e:
        return f"⚠️ خطأ في الاتصال: {str(e)}"

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200
    return "Bot is Active!", 200

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    user_data[uid] = {'lang': 'Arabic', 'count': 0}
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*[telebot.types.KeyboardButton(l) for l in LANG_CONFIG.keys()])
    bot.reply_to(message, "🚀 أهلاً بك! تم تفعيل المفتاح الجديد. اختر لغة التدقيق:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in LANG_CONFIG.keys())
def set_lang(message):
    uid = message.from_user.id
    if uid not in user_data: user_data[uid] = {'count': 0}
    user_data[uid]['lang'] = LANG_CONFIG[message.text]['name']
    bot.reply_to(message, LANG_CONFIG[message.text]['msg'])

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    if uid not in user_data: user_data[uid] = {'lang': 'Arabic', 'count': 0}
    
    bot.send_chat_action(message.chat.id, 'typing')
    result = ask_ai_api(message.text, user_data[uid]['lang'])
    bot.reply_to(message, f"✨ النتيجة:\n\n{result}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True)
