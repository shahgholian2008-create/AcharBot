import os
from aiogram import types
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from states import PhotoStates
from PIL import Image, ImageFilter, ImageEnhance
import random

async def edit_photo_with_text(message: types.Message, state: FSMContext):
    await state.set_state(PhotoStates.waiting_for_edit_text)
    await message.answer("📤 لطفاً عکس خود را ارسال کنید تا آن را ویرایش کنم.")

async def handle_edit_photo(message: types.Message, state: FSMContext, bot):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = f"temp_{photo.file_id}.jpg"
    await bot.download_file(file.file_path, file_path)

    await state.update_data(photo_path=file_path)
    await state.set_state(PhotoStates.waiting_for_edit_prompt)
    await message.answer(
        "✏️ حالا دستور متنی خود را وارد کنید.\n\n"
        "🔹 دستورات قابل استفاده:\n"
        "• کارتونی\n"
        "• آبرنگ\n"
        "• سیاه و سفید\n"
        "• وضوح بالا\n"
        "• محو\n"
        "• قدیمی\n"
        "• رنگارنگ"
    )

async def handle_edit_prompt(message: types.Message, state: FSMContext):
    prompt = message.text.lower().strip()
    await message.answer("⏳ در حال ویرایش عکس...")

    data = await state.get_data()
    file_path = data.get('photo_path')

    if not file_path or not os.path.exists(file_path):
        await message.answer("❌ خطا: عکس پیدا نشد.")
        await state.clear()
        return

    try:
        image = Image.open(file_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # کارتونی
        if "کارتونی" in prompt or "cartoon" in prompt:
            image = image.quantize(colors=16).convert('RGB')
            image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            image = image.filter(ImageFilter.SMOOTH)
        
        # آبرنگ
        elif "آبرنگ" in prompt or "watercolor" in prompt:
            image = image.filter(ImageFilter.GaussianBlur(radius=3))
        
        # سیاه و سفید
        elif "سیاه" in prompt and "سفید" in prompt:
            image = image.convert('L').convert('RGB')
        
        # وضوح بالا
        elif "وضوح" in prompt or "sharp" in prompt:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(3.5)
        
        # محو
        elif "محو" in prompt or "blur" in prompt:
            image = image.filter(ImageFilter.GaussianBlur(radius=10))
        
        # قدیمی
        elif "قدیمی" in prompt or "vintage" in prompt:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(0.4)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(0.6)
            width, height = image.size
            pixels = image.load()
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
        
        # رنگارنگ
        elif "رنگارنگ" in prompt or "colorful" in prompt:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(2.5)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
        # ترمیم
        elif "ترمیم" in prompt or "restore" in prompt or "بازسازی" in prompt:
            image = await restore_image(file_path)
            if image:
                output_path = image
            else:
                await message.answer("❌ خطا در ترمیم عکس. لطفاً دوباره تلاش کنید.")
                await state.clear()
                return
        
        else:
            await message.answer("❌ دستور شما تشخیص داده نشد.")
            await state.clear()
            return
        
        output_path = f"edited_{os.path.basename(file_path)}"
        image.save(output_path, quality=95)
        
        await message.answer("✅ عکس ویرایش‌شده:")
        await message.answer_photo(photo=FSInputFile(output_path))
        os.remove(output_path)
        
    except Exception as e:
        await message.answer(f"❌ خطا: {str(e)}")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    await state.clear()
    
    
async def restore_photo(message: types.Message, state: FSMContext):
    """دکمه ترمیم عکس"""
    await state.set_state(PhotoStates.waiting_for_enhance)
    await message.answer("📤 لطفاً عکس خود را ارسال کنید تا ترمیم شود.")

async def handle_restore(message: types.Message, state: FSMContext, bot):
    """پردازش ترمیم عکس"""
    await message.answer("⏳ در حال ترمیم عکس...")

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = f"temp_{photo.file_id}.jpg"
    await bot.download_file(file.file_path, file_path)

    try:
        from utils.ai_utils import restore_image
        result_path = await restore_image(file_path)
        
        if result_path and os.path.exists(result_path):
            await message.answer("✅ عکس ترمیم‌شده:")
            await message.answer_photo(photo=FSInputFile(result_path))
            os.remove(result_path)
        else:
            await message.answer("❌ خطا در ترمیم عکس. لطفاً دوباره تلاش کنید.")
    except Exception as e:
        await message.answer(f"❌ خطا: {str(e)}")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    await state.clear()