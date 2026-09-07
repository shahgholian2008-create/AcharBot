import os
import time
import base64
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import aiohttp
from google import genai
from google.genai import types

# ==========================================
# ========== تنظیمات اولیه ==========
# ==========================================

# تنظیم مسیر Tesseract (برای ویندوز)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ==========================================
# ========== Gemini (سوال متنی) ==========
# ==========================================

async def ask_gemini_text(prompt: str, api_key: str) -> str:
    """ارسال سوال متنی به Gemini"""
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ خطا: {str(e)}"

# ==========================================
# ========== Gemini (تحلیل عکس) ==========
# ==========================================

async def ask_gemini_about_image(file_path: str, prompt: str, api_key: str) -> str:
    """تحلیل عکس با Gemini"""
    try:
        client = genai.Client(api_key=api_key)
        
        # خواندن عکس
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                prompt
            ]
        )
        return response.text
    except Exception as e:
        if "API key" in str(e) or "billing" in str(e).lower():
            return "⚠️ تحلیل عکس با Gemini نیاز به تنظیمات اضافی دارد. در حال استفاده از روش جایگزین..."
        return f"❌ خطا: {str(e)}"

# ==========================================
# ========== Tesseract (استخراج متن) ==========
# ==========================================

async def extract_text_tesseract(file_path: str) -> str:
    """استخراج متن از عکس با Tesseract (با بهبود کیفیت)"""
    try:
        image = Image.open(file_path)
        image = image.convert('L')
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        text = pytesseract.image_to_string(
            image,
            lang='fas+eng',
            config='--psm 6'
        )
        
        text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
        
        if text:
            return f"📝 متن استخراج‌شده:\n\n{text}"
        else:
            return "❌ هیچ متنی در این عکس پیدا نشد."
            
    except Exception as e:
        return f"❌ خطا در Tesseract: {str(e)}"

# ==========================================
# ========== ترمیم عکس با DeepAI ==========
# ==========================================

async def restore_image_deepai(file_path: str) -> str:
    """ترمیم عکس با DeepAI (رایگان)"""
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()
        
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field('image', image_data, filename='image.jpg')
            
            async with session.post(
                'https://api.deepai.org/api/torch-sr',
                data=form_data,
                timeout=60
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    output_url = data.get('output_url')
                    
                    if output_url:
                        async with session.get(output_url) as img_response:
                            if img_response.status == 200:
                                output_path = f"restored_{os.path.basename(file_path)}"
                                with open(output_path, 'wb') as f:
                                    f.write(await img_response.read())
                                return output_path
                return None
    except Exception as e:
        print(f"❌ خطا در ترمیم عکس با DeepAI: {e}")
        return None

# ==========================================
# ========== ترمیم عکس با Pillow ==========
# ==========================================

async def restore_image_pillow(file_path: str) -> str:
    """ترمیم عکس با Pillow (بدون API)"""
    try:
        image = Image.open(file_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.5)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        output_path = f"restored_{os.path.basename(file_path)}"
        image.save(output_path, quality=95)
        return output_path
    except Exception as e:
        print(f"❌ خطا در ترمیم با Pillow: {e}")
        return None

# ==========================================
# ========== تابع اصلی ترمیم عکس ==========
# ==========================================

async def restore_image(file_path: str) -> str:
    """ترمیم عکس - ابتدا با DeepAI، در صورت خطا با Pillow"""
    result = await restore_image_deepai(file_path)
    if result:
        return result
    return await restore_image_pillow(file_path)

# ==========================================
# ========== تحلیل ترکیبی عکس ==========
# ==========================================

async def analyze_image(file_path: str, prompt: str, api_key: str) -> str:
    """تحلیل عکس با ترکیب Gemini و Tesseract"""
    gemini_result = await ask_gemini_about_image(file_path, prompt, api_key)
    
    if "نیاز به تنظیمات اضافی" in gemini_result or "API key" in gemini_result:
        text = await extract_text_tesseract(file_path)
        
        if "متن" in prompt or "text" in prompt or "بخوان" in prompt:
            return text
        
        return f"⚠️ تحلیل هوش مصنوعی در دسترس نیست.\n\n{text}"
    
    return gemini_result