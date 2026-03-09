import telebot
import requests
from flask import Flask, request

# --- الإعدادات (المفتاح والتوكن الخاص بك) ---
TELEGRAM_TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
GEMINI_KEY = 'AIzaSyDH7pZmRT1LWc4oDepiOKYF8Q5YXxvU_28'
MODEL_NAME = "gemini-1.5-flash"

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)
user_data = {}

# قائمة اللغات الموسعة ورسائل التأكيد بكل لغة
LANG_CONFIG = {
    'العربية 🇪🇬': {'name': 'Arabic', 'msg': '✅ تم تفعيل التدقيق باللغة العربية. أرسل نصك الآن.'},
    'English 🇺🇸': {'name': 'English', 'msg': '✅ English proofreading enabled. Send your text now.'},
    'Русский 🇷🇺': {'name': 'Russian', 'msg': '✅ Проверка русского языка включена. Отправьте текст.'},
    '中文 🇨🇳': {'name': 'Chinese', 'msg': '✅ 中文校对已启用。请发送您的文本。'},
    'עברית 🇮🇱': {'name': 'Hebrew', 'msg': '✅ בדיקת עברית הופעלה. שלח את הטקסט שלך.'},
    'فارسی 🇮🇷': {'name': 'Persian', 'msg': '✅ ویرایش فارسی فعال شد. متن خود را بفرستید.'},
    'Français 🇫🇷': {'name': 'French', 'msg': '✅ Correction française activée. Envoyez votre texte.'}
}

def ask_ai_api(text, lang):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": f"You are a professional proofreader. Correct all errors in the following {lang} text and return ONLY the corrected text: {text}"}]
        }]
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        res_json = response.json()
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        return "⚠️ عذراً، واجه المحرك مشكلة في معالجة النص."
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
    buttons = [telebot.types.KeyboardButton(l) for l in LANG_CONFIG.keys()]
    markup.add(*buttons)
    
    bot.reply_to(message, "🚀 أهلاً بك! اختر لغة التدقيق من القائمة أدناه:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in LANG_CONFIG.keys())
def set_lang(message):
    uid = message.from_user.id
    if uid not in user_data: 
        user_data[uid] = {'count': 0}
    
    selected_lang = message.text
    user_data[uid]['lang'] = LANG_CONFIG[selected_lang]['name']
    
    # الرد بنفس اللغة المختارة
    bot.reply_to(message, LANG_CONFIG[selected_lang]['msg'])

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    if uid not in user_data: 
        user_data[uid] = {'lang': 'Arabic', 'count': 0}
    
    words_count = len(message.text.split())
    if user_data[uid]['count'] >= 20:
        bot.reply_to(message, "⚠️ انتهت الفترة المجانية (20 كلمة). تواصل مع @orna0921")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    result = ask_ai_api(message.text, user_data[uid]['lang'])
    user_data[uid]['count'] += words_count
    
    bot.reply_to(message, f"✨ النتيجة:\n\n{result}\n\n📊 استهلاكك: ({user_data[uid]['count']}/20)")

if __name__ == "__main__":
    # هذا الجزء يعمل فقط إذا شغلت الملف يدوياً في Termux
    bot.remove_webhook()
    bot.polling(none_stop=True)
