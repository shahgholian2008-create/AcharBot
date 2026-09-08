import asyncio
import logging
import json
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# اضافه کردن مسیر فعلی به sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers import start, enhance, remove_bg, edit, ai_handler as ai
from states import PhotoStates

# ========== بارگذاری توکن ==========
# اولویت با متغیر محیطی است (برای سرورهایی مثل Render)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# اگر متغیر محیطی وجود نداشت، از config.json بخوان (برای محیط محلی)
if not TOKEN:
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            TOKEN = config.get("telegram_token")
    except FileNotFoundError:
        print("❌ فایل config.json پیدا نشد!")
    except KeyError:
        print("❌ کلید telegram_token در config.json وجود ندارد!")

# اگر هیچ توکنی پیدا نشد، برنامه را متوقف کن
if not TOKEN:
    raise ValueError("❌ توکن ربات پیدا نشد! متغیر TELEGRAM_TOKEN را تنظیم کنید یا فایل config.json را بررسی کنید.")

# ========== تنظیمات اولیه ==========
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

# ==========================================
# ========== ثبت هندلرها ==========
# ==========================================

# 1. منو و راهنما
dp.message.register(start.start_command, Command("start"))
dp.message.register(start.help_command, lambda m: m.text == "ℹ️ راهنما")

# 2. هوش مصنوعی (AI)
dp.message.register(ai.ai_menu, lambda m: m.text == "🤖 سوال از هوش مصنوعی")
dp.message.register(ai.ai_text, Command("ask"))
dp.message.register(ai.handle_ai_text, PhotoStates.waiting_for_gemini_question)
dp.message.register(ai.ai_image, Command("askimage"))
dp.message.register(ai.handle_ai_image, PhotoStates.waiting_for_gemini_image)
dp.message.register(ai.handle_ai_image_question, PhotoStates.waiting_for_edit_prompt)

# 3. افزایش کیفیت
dp.message.register(enhance.enhance_photo, lambda m: m.text == "📸 افزایش کیفیت")
dp.message.register(enhance.handle_enhance, PhotoStates.waiting_for_enhance)

# 4. حذف پس‌زمینه
dp.message.register(remove_bg.remove_bg_photo, lambda m: m.text == "🖼️ حذف پس‌زمینه")
dp.message.register(remove_bg.handle_removebg, PhotoStates.waiting_for_removebg)

# 5. ویرایش با متن
dp.message.register(edit.edit_photo_with_text, lambda m: m.text == "🎨 ویرایش با متن")
dp.message.register(edit.handle_edit_photo, PhotoStates.waiting_for_edit_text)
dp.message.register(edit.handle_edit_prompt, PhotoStates.waiting_for_edit_prompt)

# 6. ترمیم عکس
dp.message.register(edit.restore_photo, lambda m: m.text == "🛠️ ترمیم عکس")
dp.message.register(edit.handle_restore, PhotoStates.waiting_for_enhance)

# 7. پیام‌های نامشخص (آخرین هندلر)
@dp.message()
async def unknown_message(message: types.Message, state):
    await state.clear()
    await message.answer("❌ لطفاً از دکمه‌های منو استفاده کنید یا /start را بزنید.")

# ==========================================
# ========== اجرای ربات ==========
# ==========================================

async def main():
    print("🤖 ربات هوش مصنوعی Achar France روشن شد...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
