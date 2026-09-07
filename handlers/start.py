from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📸 افزایش کیفیت")],
            [types.KeyboardButton(text="🖼️ حذف پس‌زمینه")],
            [types.KeyboardButton(text="🎨 ویرایش با متن")],
            [types.KeyboardButton(text="🛠️ ترمیم عکس")],
            [types.KeyboardButton(text="🤖 سوال از هوش مصنوعی")],
            [types.KeyboardButton(text="ℹ️ راهنما")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "🤖 به ربات هوش مصنوعی Achar France خوش آمدید!\n\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=keyboard
    )

async def help_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📖 **راهنمای کامل ربات هوش مصنوعی Achar France**\n\n"
        "🔹 **📸 افزایش کیفیت**\n"
        "   عکس خود را بفرستید تا کیفیت آن افزایش یابد.\n\n"
        "🔹 **🖼️ حذف پس‌زمینه**\n"
        "   عکس خود را بفرستید تا پس‌زمینه آن به‌طور خودکار حذف شود.\n\n"
        "🔹 **🎨 ویرایش با متن**\n"
        "   عکس خود را بفرستید و سپس یکی از دستورات زیر را وارد کنید:\n"
        "   • کارتونی\n"
        "   • آبرنگ\n"
        "   • سیاه و سفید\n"
        "   • وضوح بالا\n"
        "   • محو\n"
        "   • قدیمی\n"
        "   • رنگارنگ\n\n"
        "🔹 **🛠️ ترمیم عکس**\n"
        "   عکس‌های قدیمی، کم‌کیفیت یا خراب را ترمیم و بازیابی می‌کند.\n"
        "   (از ترکیب هوش مصنوعی DeepAI و پردازش محلی استفاده می‌کند)\n\n"
        "🔹 **🤖 سوال از هوش مصنوعی**\n"
        "   از هوش مصنوعی سوال بپرسید یا درباره عکس سوال کنید.\n"
        "   • `/ask` : سوال متنی بپرسید.\n"
        "   • `/askimage` : عکس بفرستید و درباره آن سوال کنید.\n"
        "   • برای استخراج متن از عکس، عبارت 'متن' را بپرسید.\n\n"
        "🔹 **ℹ️ راهنما**\n"
        "   نمایش همین پیام راهنما.\n\n"
        "---\n"
        "💡 **نکته:** تمام پردازش‌ها روی سرورهای امن انجام می‌شود و عکس‌ها پس از پردازش حذف می‌شوند."
    )