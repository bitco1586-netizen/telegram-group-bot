# 🤖 ربات مدیریت گروه تلگرام

یک ربات کامل و حرفه‌ای برای مدیریت گروه‌های تلگرامی با امکانات پیشرفته.

## ✨ امکانات

### 👮 مدیریت اعضا
- **بن/آنبن** کردن کاربران
- **سایلنت/آن‌سایلنت** کاربران
- **اخطار** به کاربران (3 اخطار = بن خودکار)

### 🛡️ امنیت
- **ضد اسپم خودکار** - تشخیص و حذف پیام‌های اسپم
- **ضد لینک** - جلوگیری از ارسال لینک در گروه
- **مدیریت عضو جدید** - خوش‌آمدگویی خودکار

### 📋 ابزارها
- نمایش قوانین گروه
- اطلاعات گروه
- پین/آنپین پیام
- تنظیمات قابل تغییر

## 📦 نصب

### 1. نصب پایتون
```bash
# بررسی نسخه پایتون
python3 --version
```

### 2. نصب وابستگی‌ها
```bash
cd telegram-group-bot
pip install -r requirements.txt
```

### 3. تنظیم توکن
توکن ربات در فایل `config.py` تنظیم شده است.

### 4. اجرا
```bash
python bot.py
```

## 🚀 آپلود روی سرور

### روش 1: استفاده از VPS (پیشنهادی)

#### مرحله 1: انتخاب VPS
خدمات پیشنهادی:
- **DigitalOcean** (referral: digitalocean.com)
- **Vultr** (vultr.com)
- **Linode** (linode.com)

#### مرحله 2: اتصال SSH
```bash
ssh root@YOUR_SERVER_IP
```

#### مرحله 3: نصب پایتون
```bash
# Ubuntu/Debian
apt update && apt upgrade -y
apt install python3 python3-pip git -y

# CentOS
yum update -y
yum install python3 python3-pip git -y
```

#### مرحله 4: آپلود فایل‌ها
```bash
# کلون کردن از GitHub
git clone https://github.com/YOUR_USERNAME/telegram-group-bot.git
cd telegram-group-bot

# یا آپلود دستی با SCP
scp -r telegram-group-bot root@YOUR_SERVER_IP:/root/
```

#### مرحله 5: نصب و اجرا
```bash
pip3 install -r requirements.txt
python3 bot.py
```

#### مرحله 6: اجرا در پس‌زمینه با screen
```bash
# نصب screen
apt install screen -y

# ایجاد session جدید
screen -S telegram-bot

# اجرای ربات
python3 bot.py

# خروج از screen (ربات در پس‌زمینه اجرا می‌شود)
# Ctrl + A + D

# بازگشت به screen
screen -r telegram-bot
```

#### مرحله 7: استفاده از systemd (روش حرفه‌ای)
```bash
# ایجاد فایل سرویس
nano /etc/systemd/system/telegram-bot.service
```

محتوای فایل:
```ini
[Unit]
Description=Telegram Group Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/telegram-group-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# فعال‌سازی سرویس
systemctl daemon-reload
systemctl enable telegram-bot
systemctl start telegram-bot

# بررسی وضعیت
systemctl status telegram-bot
```

### روش 2: استفاده از Render.com (رایگان)

1. ساخت اکانت در [render.com](https://render.com)
2. ایجاد Web Service جدید
3. اتصال به GitHub repository
4. تنظیم Build Command: `pip install -r requirements.txt`
5. تنظیم Start Command: `python bot.py`

### روش 3: استفاده از Railway.app (رایگان)

1. ساخت اکانت در [railway.app](https://railway.app)
2. Deploy from GitHub
3. تنظیمات مشابه Render

## 📝 دستورات ربات

### دستورات عمومی
| دستور | توضیحات |
|-------|---------|
| `/start` | شروع ربات |
| `/help` | راهنما |
| `/rules` | قوانین گروه |
| `/info` | اطلاعات گروه |
| `/settings` | تنظیمات گروه |

### دستورات ادمین
| دستور | توضیحات |
|-------|---------|
| `/ban [یوزرنیم/ریپلای]` | بن کردن |
| `/unban [یوزرنیم/ریپلای]` | آنبن کردن |
| `/mute [یوزرنیم/ریپلای]` | سایلنت |
| `/unmute [یوزرنیم/ریپلای]` | حذف سایلنت |
| `/warn [یوزرنیم/ریپلای]` | اخطار |
| `/resetwarn [یوزرنیم/ریپلای]` | ریست اخطارها |
| `/warnings [یوزرنیم/ریپلای]` | نمایش اخطارها |
| `/pin` | پین پیام |
| `/unpin` | آنپین پیام |

### تنظیمات
| دستور | توضیحات |
|-------|---------|
| `/welcome on/off` | خوش‌آمدگویی |
| `/antispam on/off` | ضد اسپم |
| `/antilink on/off` | ضد لینک |

## 🔧 تنظیمات پیشرفته

فایل `config.py` را ویرایش کنید:

```python
# توکن ربات
BOT_TOKEN = "YOUR_BOT_TOKEN"

# تنظیمات ضد اسپم
SPAM_THRESHOLD = 5  # تعداد پیام
SPAM_TIME_WINDOW = 10  # ثانیه

# پیام خوش‌آمدگویی
WELCOME_MESSAGE = "..."
```

## 📁 ساختار پروژه

```
telegram-group-bot/
├── bot.py          # فایل اصلی ربات
├── config.py       # تنظیمات
├── requirements.txt # وابستگی‌ها
└── README.md       # مستندات
```

## ⚠️ نکات مهم

1. **امنیت توکن**: توکن ربات را در جای امن نگه دارید
2. **دسترسی ربات**: ربات باید ادمین گروه باشد
3. **حریم خصوصی**: ربات را در گروه‌های خصوصی استفاده کنید

## 🐛 رفع مشکلات رایج

### خطای imports
```bash
pip install python-telegram-bot --upgrade
```

### ربات کار نمی‌کند
- بررسی کنید ربات ادمین گروه هست
- بررسی کنید توکن صحیح است
- لاگ‌ها را بررسی کنید

### خطای permission
- ربات باید دسترسی حذف پیام داشته باشد
- ربات باید دسترسی بن کردن داشته باشد

## 📜 لایسنس

این پروژه رایگان و متن‌باز است.

---

ساخته شده با ❤️ برای مدیریت بهتر گروه‌های تلگرامی