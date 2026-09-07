from aiogram import types
from aiogram.fsm.context import FSMContext
from states import PhotoStates
from utils.ai_utils import ask_gemini_text, analyze_image, extract_text_tesseract
import os
import json

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

AI_API_KEY = config.get("gemini_api_key")

async def ai_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🤖 حالت سوال از هوش مصنوعی فعال شد.\n\n"
        "📝 برای سوال متنی: /ask\n"
        "🖼️ برای تحلیل عکس: /askimage\n"
        "🔹 برای استخراج متن از عکس، عبارت 'متن' را بپرسید.\n"
        "🔹 اگر تحلیل عکس با مشکل مواجه شد، از روش جایگزین استفاده می‌شود."
    )

async def ai_text(message: types.Message, state: FSMContext):
    await state.set_state(PhotoStates.waiting_for_gemini_question)
    await message.answer("📝 سوال خود را بفرستید.")

async def handle_ai_text(message: types.Message, state: FSMContext):
    await message.answer("⏳ در حال فکر کردن...")
    answer = await ask_gemini_text(message.text, AI_API_KEY)
    await message.answer(f"🤖 پاسخ هوش مصنوعی:\n\n{answer}")
    await state.clear()

async def ai_image(message: types.Message, state: FSMContext):
    await state.set_state(PhotoStates.waiting_for_gemini_image)
    await message.answer("🖼️ عکس خود را بفرستید.")

async def handle_ai_image(message: types.Message, state: FSMContext, bot):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = f"temp_ai_{photo.file_id}.jpg"
    await bot.download_file(file.file_path, file_path)
    
    await state.update_data(image_path=file_path)
    await state.set_state(PhotoStates.waiting_for_edit_prompt)
    await message.answer(
        "✏️ حالا سوال خود را بپرسید.\n"
        "مثلاً: 'در این عکس چه چیزی وجود دارد؟' یا 'متن این عکس را بخوان'"
    )

async def handle_ai_image_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    file_path = data.get('image_path')
    
    if not file_path or not os.path.exists(file_path):
        await message.answer("❌ خطا: عکس پیدا نشد.")
        await state.clear()
        return
    
    user_question = message.text.lower().strip()
    await message.answer("⏳ در حال تحلیل عکس...")
    
    # استفاده از تابع ترکیبی برای تحلیل عکس
    answer = await analyze_image(file_path, user_question, AI_API_KEY)
    
    await message.answer(f"🤖 پاسخ هوش مصنوعی:\n\n{answer}")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    await state.clear()