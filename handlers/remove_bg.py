import os
from aiogram import types
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from states import PhotoStates
import aiohttp

# ========== خواندن کلید از متغیر محیطی ==========
REMOVEBG_API_KEY = os.environ.get("REMOVEBG_API_KEY")

if not REMOVEBG_API_KEY:
    raise ValueError("❌ REMOVEBG_API_KEY not found in environment variables")

async def remove_bg_photo(message: types.Message, state: FSMContext):
    await state.set_state(PhotoStates.waiting_for_removebg)
    await message.answer("📤 لطفاً عکس خود را ارسال کنید تا پس‌زمینه حذف شود.")

async def handle_removebg(message: types.Message, state: FSMContext, bot):
    await message.answer("⏳ در حال حذف پس‌زمینه...")

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = f"temp_{photo.file_id}.jpg"
    await bot.download_file(file.file_path, file_path)

    try:
        # ✅ استفاده از پروکسی PythonAnywhere
        proxy_url = 'http://proxy.server:3128'
        
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                files = {'image_file': f}
                headers = {'X-Api-Key': REMOVEBG_API_KEY}
                async with session.post(
                    'https://api.remove.bg/v1.0/removebg',
                    headers=headers,
                    data=files,
                    proxy=proxy_url,  # ✅ اضافه کردن پروکسی
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result_data = await response.read()
                        output_path = f"nobg_{os.path.basename(file_path)}"
                        with open(output_path, 'wb') as f:
                            f.write(result_data)
                        
                        await message.answer("✅ عکس با پس‌زمینه حذف‌شده:")
                        await message.answer_photo(photo=FSInputFile(output_path))
                        os.remove(output_path)
                    else:
                        error_text = await response.text()
                        await message.answer(f"❌ خطا: {error_text}")
    except Exception as e:
        await message.answer(f"❌ خطا: {str(e)}")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    await state.clear()