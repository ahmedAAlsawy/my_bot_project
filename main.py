import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from flask import Flask
from threading import Thread

# --- 1. خادم الويب للبقاء حياً ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    # تشغيل سيرفر ويب بسيط لاستقبال تنبيهات الاستضافة
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعدادات البوت ---
# التوكن الخاص بك
API_TOKEN = '8703815623:AAHCNxFc6zYLTV6Qgcc0HOmKmVDKqkGjlR4'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# معالج أمر /start
@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    await message.answer(f"أهلاً يا {message.from_user.full_name}! 🚀\nبوتك يعمل الآن بنجاح على النسخة الحديثة.")

# معالج الرسائل النصية (Echo)
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"أنت أرسلت: {message.text}")

# --- 3. الدالة الرئيسية للتشغيل ---
async def start_bot():
    keep_alive()
    print("البوت بدأ في استقبال الرسائل... جربه الآن في تليجرام!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        print("تم إيقاف البوت.")
