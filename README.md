# 🤖 AcharBot — ربات هوش مصنوعی تلگرام

ربات تلگرام حرفه‌ای برای پردازش، ویرایش و بهبود عکس با استفاده از هوش مصنوعی.

---

## ✨ قابلیت‌ها

| قابلیت | توضیح |
|--------|-------|
| 🤖 سوال از هوش مصنوعی | پرسیدن سوال متنی یا تصویری از Gemini |
| 📸 افزایش کیفیت عکس | بهبود کیفیت و وضوح تصاویر |
| 🎨 ویرایش با متن | ویرایش عکس با دستور متنی (شامل حذف پس‌زمینه) |

---

## 🛠 تکنولوژی‌ها

- Python 3.10+
- aiogram 3.x — فریمورک ربات تلگرام
- Flask — وب‌سرور برای Webhook
- Google Gemini API — هوش مصنوعی
- RemoveBG API — حذف پس‌زمینه
- PythonAnywhere — هاست

---

## 📁 ساختار پروژه

AcharBot/
├── flask_app.py           # فایل اصلی (Webhook + Flask)
├── states.py              # وضعیت‌های FSM
├── config.json            # تنظیمات (در .gitignore)
├── requirements.txt       # کتابخانه‌های مورد نیاز
├── .gitignore
├── README.md
├── handlers/              # هندلرهای ربات
│   ├── start.py
│   ├── ai_handler.py
│   ├── enhance.py
│   ├── edit.py
│   └── remove_bg.py
└── utils/                 # ابزارهای کمکی
    └── ai_utils.py

---

## 🚀 نصب و اجرا

### ۱. کلون کردن پروژه
git clone https://github.com/shahgholian2008-create/AcharBot.git
cd AcharBot

### ۲. نصب کتابخانه‌ها
pip install -r requirements.txt

### ۳. ساخت فایل config.json
{
  "telegram_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "removebg_api_key": "YOUR_REMOVEBG_API_KEY",
  "gemini_api_key": "YOUR_GEMINI_API_KEY"
}

### ۴. اجرا
python flask_app.py

---

## 🔐 امنیت

- ✅ توکن‌ها و کلیدهای API در config.json نگهداری می‌شوند
- ✅ config.json در .gitignore قرار دارد و به GitHub آپلود نمی‌شود
- ✅ از فایل config.example.json برای نمونه استفاده کنید

---

## 🌐 دیپلوی

این ربات روی PythonAnywhere با استفاده از Webhook اجرا می‌شود.

Webhook URL: https://KtMir.pythonanywhere.com/webhook

---

## 👩‍💻 توسعه‌دهنده

KtMir — در حال یادگیری پایتون و فریلنسری

GitHub: @shahgholian2008-create

---

## 📄 مجوز

این پروژه برای اهداف آموزشی و شخصی توسعه یافته است.

---

## ⭐ حمایت

اگه این پروژه برات مفید بود، یه ⭐ بهش بده!
