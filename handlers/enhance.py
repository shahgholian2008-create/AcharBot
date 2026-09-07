import os
from aiogram import types
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from states import PhotoStates
from PIL import Image, ImageEnhance

async def enhance_photo(message: types.Message, state: FSMContext):
    await state.set_state(PhotoStates.waiting_for_enhance)
    await message.answer("📤 لطفاً عکس خود را ارسال کنید تا کیفیت آن افزایش یابد.")

async def handle_enhance(message: types.Message, state: FSMContext, bot):
    await message.answer("⏳ در حال افزایش کیفیت عکس...")

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = f"temp_{photo.file_id}.jpg"
    await bot.download_file(file.file_path, file_path)

    try:
        image = Image.open(file_path)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)
        
        output_path = f"enhanced_{os.path.basename(file_path)}"
        image.save(output_path, quality=95)
        
        await message.answer("✅ عکس با کیفیت بالا:")
        await message.answer_photo(photo=FSInputFile(output_path))
        os.remove(output_path)
    except Exception as e:
        await message.answer(f"❌ خطا: {str(e)}")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    await state.clear()