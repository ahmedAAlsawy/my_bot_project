import telebot
import requests
from flask import Flask, request

# --- الإعدادات (تأكد من بقاء التوكن والمفتاح كما هما) ---
TELEGRAM_TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
GEMINI_KEY = 'AIzaSyDH7pZmRT1LWc4oDepiOKYF8Q5YXxvU_28'
# التحديث: استخدام المسمى الأكثر استقراراً
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
    # التحديث: الانتقال إلى v1 بدلاً من v1beta لحل مشكلة الـ 404
    url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={GEMINI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Correct all errors in the following {lang} text and return ONLY the result: {text}"}]
        }]
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        res_json = response.json()
        
        # حالة النجاح
        if response.status_code == 200 and 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # تحليل الأخطاء بدقة (Diagnostic Mode)
        status = response.status_code
        error_info = res_json.get('error', {})
        error_msg = error_info.get('message', 'خطأ غير معروف')
        error_status = error_info.get('status', 'UNKNOWN')
        
        if status == 404:
            return f"❌ خطأ (404): الموديل غير مدعوم في هذا الإصدار. جرب تغيير MODEL_NAME إلى gemini-1.5-flash-latest"
        elif status == 403:
            return f"❌ خطأ في الحساب (403): {error_msg}\nتأكد من تفعيل Gemini API في Google AI Studio."
        elif status == 400:
            return f"❌ خطأ في البيانات (400): {error_msg}"
        else:
            return f"❌ خطأ تقني ({status}): {error_status}\nالرسالة: {error_msg}"

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
    bot.reply_to(message, "🚀 أهلاً بك! البوت الآن يعمل بالإصدار المستقر. اختر اللغة:", reply_markup=markup)

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
