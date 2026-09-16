import os
import sys
import json
import logging
import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

# ========== بارگذاری تنظیمات از config.json ==========
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

os.environ["TELEGRAM_TOKEN"] = config["telegram_token"]
os.environ["REMOVEBG_API_KEY"] = config["removebg_api_key"]
os.environ["GEMINI_API_KEY"] = config["gemini_api_key"]

# ========== تنظیم مسیرها ==========
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ========== وارد کردن هندلرها ==========
from handlers import start, enhance, remove_bg, edit, ai_handler as ai
from states import PhotoStates

# ========== بارگذاری توکن ==========
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن ربات پیدا نشد!")

# ========== تنظیمات اولیه ==========
logging.basicConfig(level=logging.INFO)

# ✅ تنظیم پروکسی برای PythonAnywhere
proxy_url = 'http://proxy.server:3128'
session = AiohttpSession(proxy=proxy_url)

bot = Bot(token=TOKEN, session=session)

# ✅ اضافه کردن MemoryStorage برای حفظ وضعیت
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========== ثبت هندلرها ==========
dp.message.register(start.start_command, Command("start"))
dp.message.register(start.help_command, lambda m: m.text == "ℹ️ راهنما")

# ✅ هندلرهای افزایش کیفیت
dp.message.register(enhance.enhance_photo, lambda m: m.text == "📸 افزایش کیفیت")
dp.message.register(enhance.handle_enhance, PhotoStates.waiting_for_enhance)

# ✅ هندلرهای حذف پس‌زمینه
dp.message.register(remove_bg.remove_bg_photo, lambda m: m.text == "🖼️ حذف پس‌زمینه")
dp.message.register(remove_bg.handle_removebg, PhotoStates.waiting_for_removebg)

# ✅ هندلرهای ویرایش با متن
dp.message.register(edit.edit_photo_with_text, lambda m: m.text == "🎨 ویرایش با متن")
dp.message.register(edit.handle_edit_photo, PhotoStates.waiting_for_edit_text)
dp.message.register(edit.handle_edit_prompt, PhotoStates.waiting_for_edit_prompt)

# ✅ هندلرهای هوش مصنوعی
dp.message.register(ai.ai_menu, lambda m: m.text == "🤖 سوال از هوش مصنوعی")
dp.message.register(ai.ai_text, Command("ask"))
dp.message.register(ai.handle_ai_text, PhotoStates.waiting_for_gemini_question)
dp.message.register(ai.ai_image, Command("askimage"))
dp.message.register(ai.handle_ai_image, PhotoStates.waiting_for_gemini_image)
dp.message.register(ai.handle_ai_image_question, PhotoStates.waiting_for_gemini_image_question)

@dp.message()
async def unknown_message(message: types.Message, state):
    await state.clear()
    await message.answer("❌ لطفاً از دکمه‌های منو استفاده کنید یا /start را بزنید.")

# ========== ایجاد حلقه‌ی پایدار asyncio ==========
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# ========== ایجاد برنامه Flask ==========
app = Flask(__name__)

@app.route("/")
def index():
    return "ربات روشن است!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update_data = request.get_json(force=True)
        update = Update.model_validate(update_data, context={"bot": bot})
        loop.run_until_complete(dp.feed_update(bot, update))
    except Exception as e:
        logging.error(f"خطا در پردازش آپدیت: {e}")

    return "OK", 200