"""
🤖 ربات مدیریت گروه تلگرام
 نسخه کامل و حرفه‌ای
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ChatMemberHandler
)
from config import BOT_TOKEN, SPAM_THRESHOLD, SPAM_TIME_WINDOW, WELCOME_MESSAGE, BANNED_WORDS

# تنظیم لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دیکشنری‌های ذخیره اطلاعات
warned_users = defaultdict(int)  # تعداد اخطارها
muted_users = {}  # کاربران سایلنت شده
spam_counter = defaultdict(list)  # شمارنده اسپم
group_settings = {}  # تنظیمات گروه


def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """بررسی ادمین بودن کاربر"""
    try:
        member = context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in ['creator', 'administrator']
    except:
        return False


def is_group_admin(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """بررسی ادمین بودن در گروه"""
    try:
        member = context.bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except:
        return False


# ============================================
# دستورات مدیریتی
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع"""
    if update.message.chat.type in ['group', 'supergroup']:
        await update.message.reply_text(
            "🤖 ربات مدیریت گروه فعال شد!\n"
            "برای مشاهده دستورات: /help"
        )
    else:
        await update.message.reply_text(
            "👋 سلام! من ربات مدیریت گروه تلگرام هستم.\n\n"
            "📌 امکانات:\n"
            "• مدیریت اعضا (بن/آنبن)\n"
            "• ضد اسپم خودکار\n"
            "• ضد لینک\n"
            "• خوش‌آمدگویی\n"
            "• اخطار به کاربران\n\n"
            "🔧 برای افزودن به گروه، ادمین گروه را به @BotFather بدهید."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش راهنما"""
    help_text = """
📚 **راهنمای دستورات ربات:**

👮 **دستورات ادمین:**
• /ban [یوزرنیم/ریپلای] - بن کردن کاربر
• /unban [یوزرنیم/ریپلای] - آنبن کردن کاربر
• /mute [یوزرنیم/ریپلای] - سایلنت کردن
• /unmute [یوزرنیم/ریپلای] - حذف سایلنت
• /warn [یوزرنیم/ریپلای] - اخطار به کاربر
• /resetwarn [یوزرنیم/ریپلای] - حذف اخطارها
• /warnings [یوزرنیم/ریپلای] - نمایش اخطارها

📋 **دستورات عمومی:**
• /rules - قوانین گروه
• /info - اطلاعات گروه
• /stats - آمار گروه
• /pin - پین کردن پیام
• /unpin - آنپین کردن پیام
• /settings - تنظیمات گروه

⚙️ **تنظیمات:**
• /welcome [on/off] - خوش‌آمدگویی
• /antispam [on/off] - ضد اسپم
• /antilink [on/off] - ضد لینک

🔒 فقط ادمین‌ها می‌توانند از دستورات مدیریتی استفاده کنند.
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش قوانین"""
    rules = """
📜 **قوانین گروه:**

1️⃣ رعایت احترام و ادب
2️⃣ عدم ارسال لینک بدون اجازه
3️⃣ عدم تبلیغات
4️⃣ عدم اسپم
5️⃣ عدم ارسال محتوای نامناسب

⚠️ نقض قوانین = اخطار → بن شدن
"""
    await update.message.reply_text(rules, parse_mode='Markdown')


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات گروه"""
    chat = update.effective_chat
    info_text = f"""
📊 **اطلاعات گروه:**

🏷️ نام: {chat.title}
🆔 آیدی: `{chat.id}`
👥 تعداد اعضا: در حال دریافت...
📝 توضیحات: {chat.description or 'ندارد'}
"""
    try:
        member_count = await context.bot.get_chat_member_count(chat.id)
        info_text = info_text.replace('در حال دریافت...', str(member_count))
    except:
        pass
    
    await update.message.reply_text(info_text, parse_mode='Markdown')


# ============================================
# دستورات مدیریتی (ادمین)
# ============================================

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بن کردن کاربر"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ کاربر یافت نشد.")
        return
    
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"🚫 کاربر {user.full_name} بن شد.")
        logger.info(f"User {user.id} banned by {update.effective_user.id}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """آنبن کردن کاربر"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ کاربر یافت نشد.")
        return
    
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"✅ کاربر {user.full_name} آنبن شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")


async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """سایلنت کردن کاربر"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ کاربر یافت نشد.")
        return
    
    muted_users[user.id] = {
        'chat_id': update.effective_chat.id,
        'muted_by': update.effective_user.id,
        'time': datetime.now()
    }
    
    await update.message.reply_text(f"🔇 کاربر {user.full_name} سایلنت شد.")
    
    # حذف پیام کاربر
    try:
        await update.message.delete()
    except:
        pass


async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف سایلنت"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ کاربر یافت نشد.")
        return
    
    if user.id in muted_users:
        del muted_users[user.id]
        await update.message.reply_text(f"🔊 سایلنت {user.full_name} برداشته شد.")
    else:
        await update.message.reply_text("❌ این کاربر سایلنت نیست.")


async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اخطار به کاربر"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ کاربر یافت نشد.")
        return
    
    warned_users[user.id] += 1
    count = warned_users[user.id]
    
    warning_msg = f"⚠️ اخطار به {user.full_name}! ({count}/3)"
    
    if count >= 3:
        warning_msg += "\n🚫 تعداد اخطارها به حداکثر رسید! کاربر بن می‌شود."
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        except:
            pass
    
    await update.message.reply_text(warning_msg)


async def resetwarn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ریست اخطارها"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ کاربر یافت نشد.")
        return
    
    warned_users[user.id] = 0
    await update.message.reply_text(f"✅ اخطارهای {user.full_name} ریست شد.")


async def warnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اخطارها"""
    user = await get_target_user(update, context)
    if not user:
        user = update.effective_user
    
    count = warned_users[user.id]
    await update.message.reply_text(f"⚠️ اخطارهای {user.full_name}: {count}/3")


async def pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پین کردن پیام"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    if update.message.reply_to_message:
        await update.message.reply_to_message.pin()
        await update.message.reply_text("📌 پیام پین شد.")
    else:
        await update.message.reply_text("⚠️ لطفاً روی پیام مورد نظر ریپلای کنید.")


async def unpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """آنپین کردن پیام"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    if update.message.reply_to_message:
        await update.message.reply_to_message.unpin()
        await update.message.reply_text("📌 پین برداشته شد.")
    else:
        await context.bot.unpin_all_chat_messages(update.effective_chat.id)
        await update.message.reply_text("📌 همه پین‌ها برداشته شد.")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیمات گروه"""
    keyboard = [
        [InlineKeyboardButton("🎉 خوش‌آمدگویی", callback_data="setting_welcome")],
        [InlineKeyboardButton("🛡️ ضد اسپم", callback_data="setting_antispam")],
        [InlineKeyboardButton("🔗 ضد لینک", callback_data="setting_antilink")],
        [InlineKeyboardButton("📊 آمار", callback_data="setting_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ **تنظیمات گروه:**\n\nیک گزینه را انتخاب کنید:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


# ============================================
# دستورات تنظیمات
# ============================================

async def welcome_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فعال/غیرفعال کردن خوش‌آمدگویی"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    chat_id = update.effective_chat.id
    if chat_id not in group_settings:
        group_settings[chat_id] = {'welcome': True, 'antispam': True, 'antilink': True}
    
    args = context.args
    if args and args[0].lower() == 'off':
        group_settings[chat_id]['welcome'] = False
        await update.message.reply_text("✅ خوش‌آمدگویی غیرفعال شد.")
    else:
        group_settings[chat_id]['welcome'] = True
        await update.message.reply_text("✅ خوش‌آمدگویی فعال شد.")


async def antispam_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فعال/غیرفعال کردن ضد اسپم"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    chat_id = update.effective_chat.id
    if chat_id not in group_settings:
        group_settings[chat_id] = {'welcome': True, 'antispam': True, 'antilink': True}
    
    args = context.args
    if args and args[0].lower() == 'off':
        group_settings[chat_id]['antispam'] = False
        await update.message.reply_text("✅ ضد اسپم غیرفعال شد.")
    else:
        group_settings[chat_id]['antispam'] = True
        await update.message.reply_text("✅ ضد اسپم فعال شد.")


async def antilink_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فعال/غیرفعال کردن ضد لینک"""
    if not is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این کار را انجام دهند.")
        return
    
    chat_id = update.effective_chat.id
    if chat_id not in group_settings:
        group_settings[chat_id] = {'welcome': True, 'antispam': True, 'antilink': True}
    
    args = context.args
    if args and args[0].lower() == 'off':
        group_settings[chat_id]['antilink'] = False
        await update.message.reply_text("✅ ضد لینک غیرفعال شد.")
    else:
        group_settings[chat_id]['antilink'] = True
        await update.message.reply_text("✅ ضد لینک فعال شد.")


# ============================================
# تابع کمکی برای یافتن کاربر
# ============================================

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """یافتن کاربر هدف از ریپلای یا آرگومان"""
    # اول ریپلای را بررسی کن
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    
    # سپس آرگومان‌ها را بررسی کن
    if context.args:
        username = context.args[0].replace('@', '')
        try:
            chat = await context.bot.get_chat(f"@{username}")
            return chat
        except:
            pass
        
        # آیدی عددی
        try:
            user_id = int(context.args[0])
            chat = await context.bot.get_chat(user_id)
            return chat
        except:
            pass
    
    return None


# ============================================
# مدیریت پیام‌ها
# ============================================

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """خوش‌آمدگویی به عضو جدید"""
    chat_id = update.effective_chat.id
    
    # بررسی تنظیمات
    if chat_id not in group_settings or group_settings[chat_id].get('welcome', True):
        for member in update.message.new_chat_members:
            welcome = WELCOME_MESSAGE.format(
                name=member.full_name,
                group_name=update.effective_chat.title
            )
            await update.message.reply_text(welcome)
            
            # تنظیمات پیش‌فرض
            if chat_id not in group_settings:
                group_settings[chat_id] = {'welcome': True, 'antispam': True, 'antilink': True}


async def handle_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خروج اعضا"""
    # می‌توانید پیامی ارسال کنید
    pass


async def anti_spam_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بررسی اسپم"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if chat_id not in group_settings or not group_settings[chat_id].get('antispam', True):
        return False
    
    # بررسی ادمین
    if is_group_admin(chat_id, user_id, context):
        return False
    
    now = datetime.now()
    key = f"{chat_id}_{user_id}"
    
    # پاک کردن پیام‌های قدیمی
    spam_counter[key] = [t for t in spam_counter[key] if (now - t).seconds < SPAM_TIME_WINDOW]
    
    # اضافه کردن پیام جدید
    spam_counter[key].append(now)
    
    if len(spam_counter[key]) > SPAM_THRESHOLD:
        try:
            await update.message.delete()
            await context.bot.send_message(
                chat_id,
                f"⚠️ {update.effective_user.full_name} لطفاً اسپم نکنید!"
            )
            logger.info(f"Spam detected from user {user_id} in chat {chat_id}")
            return True
        except:
            pass
    
    return False


async def anti_link_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بررسی لینک"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if chat_id not in group_settings or not group_settings[chat_id].get('antilink', True):
        return False
    
    # بررسی ادمین
    if is_group_admin(chat_id, user_id, context):
        return False
    
    message_text = update.message.text or ""
    
    # بررسی لینک‌ها
    link_patterns = ['http://', 'https://', 't.me/', '@', 'www.']
    for pattern in link_patterns:
        if pattern in message_text.lower():
            try:
                await update.message.delete()
                await context.bot.send_message(
                    chat_id,
                    f"🔗 {update.effective_user.full_name} ارسال لینک در گروه ممنوع است!"
                )
                logger.info(f"Link detected from user {user_id} in chat {chat_id}")
                return True
            except:
                pass
            break
    
    return False


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های ورودی"""
    # بررسی سایلنت بودن کاربر
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if chat_id in muted_users:
        muted_info = muted_users[user_id]
        if muted_info['chat_id'] == chat_id:
            try:
                await update.message.delete()
                await context.bot.send_message(
                    chat_id,
                    f"🔇 {update.effective_user.full_name} شما سایلنت هستید!"
                )
            except:
                pass
            return
    
    # بررسی اسپم
    if await anti_spam_check(update, context):
        return
    
    # بررسی لینک
    if await anti_link_check(update, context):
        return


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کالبک‌ها"""
    query = update.callback_query
    
    if query.data == "setting_welcome":
        await query.answer("🎉 تنظیمات خوش‌آمدگویی")
        await query.edit_message_text("🎉 خوش‌آمدگویی: فعال")
    elif query.data == "setting_antispam":
        await query.answer("🛡️ تنظیمات ضد اسپم")
        await query.edit_message_text("🛡️ ضد اسپم: فعال")
    elif query.data == "setting_antilink":
        await query.answer("🔗 تنظیمات ضد لینک")
        await query.edit_message_text("🔗 ضد لینک: فعال")
    elif query.data == "setting_stats":
        await query.answer("📊 آمار")
        await query.edit_message_text(f"📊 آمار گروه:\n👥 تعداد اخطارها: {len(warned_users)}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاها"""
    logger.error(f"Update {update} caused error {context.error}")


# ============================================
# شروع ربات
# ============================================

def main():
    """تابع اصلی"""
    print("""
    🤖 ════════════════════════════════════════ 🤖
         ربات مدیریت گروه تلگرام
         نسخه: 1.0
    🤖 ════════════════════════════════════════ 🤖
    """)
    
    # ساخت اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()
    
    # دستورات عمومی
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rules", rules_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
    # دستورات ادمین
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("unmute", unmute_command))
    application.add_handler(CommandHandler("warn", warn_command))
    application.add_handler(CommandHandler("resetwarn", resetwarn_command))
    application.add_handler(CommandHandler("warnings", warnings_command))
    application.add_handler(CommandHandler("pin", pin_command))
    application.add_handler(CommandHandler("unpin", unpin_command))
    
    # تنظیمات
    application.add_handler(CommandHandler("welcome", welcome_toggle))
    application.add_handler(CommandHandler("antispam", antispam_toggle))
    application.add_handler(CommandHandler("antilink", antilink_toggle))
    
    # مدیریت پیام‌ها
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, 
        handle_new_member
    ))
    application.add_handler(MessageHandler(
        filters.StatusUpdate.LEFT_CHAT_MEMBER, 
        handle_left_member
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        message_handler
    ))
    
    # کالبک
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # مدیریت خطا
    application.add_error_handler(error_handler)
    
    # شروع ربات
    print("✅ ربات با موفقیت راه‌اندازی شد!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()