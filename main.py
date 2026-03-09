import telebot
from flask import Flask, request
import google.generativeai as genai

# الإعدادات الخاصة بك
TELEGRAM_TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'
GEMINI_KEY = 'AIzaSyAxs4q6ZxVWwZcD9WBkkZBYHlbRHaJdi7k'

# تهيئة الذكاء الاصطناعي
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)
user_data = {}

# قائمة اللغات المدعومة
LANGUAGES = {
    'العربية 🇪🇬': 'Arabic',
    'English 🇺🇸': 'English',
    'Русский 🇷🇺': 'Russian',
    'हिन्दी 🇮🇳': 'Hindi',
    '中文 🇨🇳': 'Chinese',
    'עברית 🇮🇱': 'Hebrew',
    'Français 🇫🇷': 'French',
    'Español 🇪🇸': 'Spanish'
}

# قاموس رسائل التأكيد باللغات المختلفة (التعديل الجديد)
CONFIRM_MESSAGES = {
    'Arabic': '✅ تم تفعيل التدقيق للغة العربية. أرسل النص الآن.',
    'English': '✅ English proofreading activated. Send your text now.',
    'Russian': '✅ Проверка русского языка активирована. Отправьте текст.',
    'Hindi': '✅ हिंदी सुधार सक्रिय हो गया है। अपना टेक्स्ट भेजें।',
    'Chinese': '✅ 中文校对已激活。请发送您的文本。',
    'Hebrew': '✅ בדיקת עברית הופעלה. שלח את הטקסט שלך כעת.',
    'French': '✅ Correction en français activée. Envoyez votre texte.',
    'Spanish': '✅ Corrección en español activada. Envía tu texto.'
}

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200
    return "Gemini Polyglot Bot is Active!", 200

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    user_data[uid] = {'lang': 'Arabic', 'lang_name': 'العربية 🇪🇬', 'count': 0}
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [telebot.types.KeyboardButton(lang) for lang in LANGUAGES.keys()]
    markup.add(*buttons)
    
    welcome_text = (
        "أهلاً بك! أنا مساعدك اللغوي الذكي 🤖\n\n"
        "أقوم بتصحيح الأخطاء الإملائية والنحوية وإعادة صياغة الجمل باحترافية.\n"
        "اختر لغة التدقيق من القائمة بالأسفل لتبدأ:"
    )
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in LANGUAGES.keys())
def set_lang(message):
    uid = message.from_user.id
    if uid not in user_data: user_data[uid] = {'count': 0}
    
    selected_lang = LANGUAGES[message.text]
    user_data[uid]['lang'] = selected_lang
    user_data[uid]['lang_name'] = message.text
    
    # اختيار رسالة التأكيد حسب اللغة المختارة
    confirm_text = CONFIRM_MESSAGES.get(selected_lang, f"✅ Activated: {message.text}")
    bot.reply_to(message, confirm_text)

@bot.message_handler(func=lambda m: True)
def handle_ai_logic(message):
    uid = message.from_user.id
    if uid not in user_data: 
        user_data[uid] = {'lang': 'Arabic', 'lang_name': 'العربية 🇪🇬', 'count': 0}
    
    words = len(message.text.split())
    
    if user_data[uid]['count'] >= 20:
        contact_msg = (
            "⚠️ عذراً، لقد انتهت الفترة المجانية.\n\n"
            "للاشتراك وفتح عدد غير محدود من الكلمات، يرجى التواصل مع المطور:\n"
            "💬 تليجرام: @orna0921\n"
            "📞 واتساب: +201069533920"
        )
        bot.reply_to(message, contact_msg)
        return

    user_data[uid]['count'] += words
    lang = user_data[uid]['lang']

    try:
        bot.send_chat_action(message.chat.id, 'typing')
        prompt = f"You are a professional proofreader. Correct any grammatical, spelling, and punctuation errors in the following text. The text is in {lang}. Rewrite it correctly in {lang} without any extra explanation or formatting. Text: {message.text}"
        
        response = model.generate_content(prompt)
        corrected_text = response.text.strip()
        
        reply = f"✨ التدقيق الذكي ({user_data[uid]['lang_name']}):\n\n{corrected_text}\n\n📊 استهلاكك: ({user_data[uid]['count']}/20 كلمة)"
        bot.reply_to(message, reply)
        
    except Exception as e:
        bot.reply_to(message, "⏳ عذراً، محرك الذكاء الاصطناعي مشغول حالياً. حاول ثانية.")
