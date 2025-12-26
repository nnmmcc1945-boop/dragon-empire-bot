# main.py
import telebot
from telebot import types
import sqlite3

# =============================
# تنظیمات اصلی
TOKEN = '8052676038:AAHDCoH_xWSUjmI-jhjQMxeow0EWc-lcXQ0'
ADMIN_ID = 647634331
GROUP_ID = "@Game_Center_Gap1"  # یوزرنیم گروه

bot = telebot.TeleBot(TOKEN)

# =============================
# دیتابیس
conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS countries (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    country_name TEXT,
    gold INTEGER,
    food INTEGER,
    wood INTEGER,
    population INTEGER,
    soldiers INTEGER,
    archers INTEGER,
    knights INTEGER,
    giants INTEGER,
    heavy_cavalry INTEGER,
    catapults INTEGER,
    ballistas INTEGER,
    dragons INTEGER
)
""")
conn.commit()

# =============================
# توابع کمکی
def get_user(user_id):
    c.execute("SELECT * FROM countries WHERE user_id=?", (user_id,))
    return c.fetchone()

def is_member(user_id):
    try:
        member = bot.get_chat_member(GROUP_ID, user_id)
        return member.status != 'left'
    except:
        return False

# =============================
# /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not is_member(user_id):
        bot.send_message(
            message.chat.id,
            f"❌ اول باید عضو گروه بشی:\n{GROUP_ID}"
        )
        return

    if get_user(user_id):
        bot.send_message(message.chat.id, "✅ قبلاً ثبت‌نام کرده‌ای.")
        return

    c.execute("""
    INSERT INTO countries VALUES (
        ?, ?, ?, 1000, 1000, 1000, 10,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    """, (
        user_id,
        message.from_user.username,
        "کشور تازه"
    ))
    conn.commit()

    bot.send_message(message.chat.id, "🎉 ثبت‌نام انجام شد!")

# =============================
# /status
@bot.message_handler(commands=['status'])
def status(message):
    data = get_user(message.from_user.id)
    if not data:
        bot.send_message(message.chat.id, "❌ ثبت‌نام نکرده‌ای.")
        return

    text = f"""
🏰 کشور: {data[2]}
💰 طلا: {data[3]}
🍎 غذا: {data[4]}
🪵 چوب: {data[5]}
👥 جمعیت: {data[6]}
⚔️ سرباز: {data[7]}
🏹 کماندار: {data[8]}
🐴 شوالیه: {data[9]}
🐉 اژدها: {data[14]}
"""
    bot.send_message(message.chat.id, text)

# =============================
# /train
@bot.message_handler(commands=['train'])
def train(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("سرباز +10", callback_data="soldier"),
        types.InlineKeyboardButton("کماندار +5", callback_data="archer"),
        types.InlineKeyboardButton("شوالیه +2", callback_data="knight")
    )
    bot.send_message(message.chat.id, "چی آموزش بدم؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    data = get_user(user_id)
    if not data:
        return

    data = list(data)

    if call.data == "soldier":
        data[7] += 10
    elif call.data == "archer":
        data[8] += 5
    elif call.data == "knight":
        data[9] += 2

    c.execute("""
    UPDATE countries SET
    soldiers=?, archers=?, knights=?
    WHERE user_id=?
    """, (data[7], data[8], data[9], user_id))
    conn.commit()

    bot.answer_callback_query(call.id, "✅ انجام شد")

# =============================
# دستورات ادمین برای دادن منابع یا ارتش (اختیاری)
@bot.message_handler(commands=['give_resources'])
def give_resources(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        gold = int(parts[2])
        food = int(parts[3])
        wood = int(parts[4])
        data = get_user(user_id)
        if not data:
            bot.reply_to(message, "کاربر یافت نشد!")
            return
        updated = list(data)
        updated[3] += gold
        updated[4] += food
        updated[5] += wood
        c.execute("""
        UPDATE countries SET
        username=?, country_name=?, gold=?, food=?, wood=?, population=?,
        soldiers=?, archers=?, knights=?, giants=?, heavy_cavalry=?, catapults=?, ballistas=?, dragons=?
        WHERE user_id=?
        """, (updated[1], updated[2], updated[3], updated[4], updated[5],
              updated[6], updated[7], updated[8], updated[9], updated[10], updated[11], updated[12], updated[13], updated[14], user_id))
        conn.commit()
        bot.reply_to(message, f"پک منابع به {data[1]} داده شد!")
    except:
        bot.reply_to(message, "فرمت دستور درست نیست. مثال: /give_resources 123456789 5000 3000 2000")

# =============================
print("بات افسانه‌ای آماده است! 🐉⚔️")
bot.infinity_polling()
        
