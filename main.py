import telebot
import requests
from flask import Flask, request

# --- الإعدادات (المفتاح الجديد الشغال) ---
TELEGRAM_TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
GEMINI_KEY = 'AIzaSyDH7pZmRT1LWc4oDepiOKYF8Q5YXxvU_28'
MODEL_NAME = "gemini-1.5-flash"

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__) # هذا السطر هو ما يطلبه Vercel (الـ Handler)

user_data = {}
LANGUAGES = {'العربية 🇪🇬': 'Arabic', 'English 🇺🇸': 'English', 'Français 🇫🇷': 'French'}

def ask_gemini_api(text, lang):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"Correct errors in {lang} and return ONLY the result: {text}"}]}]}
    try:
        response = requests.post(url, json=payload, timeout=15)
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except:
        return "⚠️ عذراً، واجه المحرك مشكلة."

# --- المسار الذي يحتاجه Vercel لاستقبال الرسائل ---
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
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[telebot.types.KeyboardButton(l) for l in LANGUAGES.keys()])
    bot.reply_to(message, "أهلاً بك! اختر لغة التدقيق من الأسفل:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in LANGUAGES.keys())
def set_lang(message):
    user_data[message.from_user.id]['lang'] = LANGUAGES[message.text]
    bot.reply_to(message, f"✅ تم تفعيل تدقيق: {message.text}")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    if uid not in user_data: user_data[uid] = {'lang': 'Arabic', 'count': 0}
    
    if user_data[uid]['count'] >= 20:
        bot.reply_to(message, "⚠️ انتهت الفترة المجانية (20 كلمة). تواصل مع @orna0921")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    result = ask_gemini_api(message.text, user_data[uid]['lang'])
    user_data[uid]['count'] += len(message.text.split())
    bot.reply_to(message, f"✨ النتيجة:\n\n{result}\n\n📊 استهلاكك: ({user_data[uid]['count']}/20)")

# هذا الجزء للتشغيل اليدوي في Termux فقط
if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True)
