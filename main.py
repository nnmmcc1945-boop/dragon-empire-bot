import telebot
from telebot import types
import sqlite3
import random
import time
import threading
from flask import Flask

# ================== تنظیمات اصلی ==================
TOKEN = "8052676038:AAHDCoH_xWSUjmI-jhjQMxeow0EWc-lcXQ0"
ADMIN_ID = 647634331

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================== سرور برای آنلاین موندن ==================
@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# ================== دیتابیس ==================
conn = sqlite3.connect("game.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    country TEXT,
    gold INTEGER,
    food INTEGER,
    wood INTEGER,
    soldiers INTEGER,
    dragons INTEGER,
    dragon_building INTEGER
)
""")

conn.commit()

# ================== کشورها ==================
COUNTRIES = {
    "هخامنشیان": "تولید طلا +۶۰٪",
    "روم باستان": "قدرت ارتش بالا",
    "مغول‌ها": "غارت قوی",
    "سامورایی": "دفاع عالی",
    "وایکینگ": "حمله سریع"
}

# ================== شروع ==================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "بی‌نام"

    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)",
            (user_id, username, None, 500, 500, 500, 10, 0, 0)
        )
        conn.commit()

    bot.send_message(
        message.chat.id,
        "👑 به بازی امپراتوری خوش آمدی!\n"
        "کشور را ادمین تعیین می‌کند.\n"
        "دستورها:\n"
        "/status\n"
        "/countries\n"
        "/attack\n"
        "/train_dragon"
    )

# ================== وضعیت ==================
@bot.message_handler(commands=['status'])
def status(message):
    user_id = message.from_user.id
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    u = c.fetchone()

    if not u:
        return

    text = (
        f"👤 کاربر: @{u[1]}\n"
        f"🏳 کشور: {u[2]}\n"
        f"💰 طلا: {u[3]}\n"
        f"🍖 غذا: {u[4]}\n"
        f"🌲 چوب: {u[5]}\n"
        f"⚔️ سرباز: {u[6]}\n"
        f"🐉 اژدها: {u[7]}\n"
        f"🏰 ساختمان اژدها: {u[8]}"
    )

    bot.send_message(message.chat.id, text)

# ================== نمایش کشورها ==================
@bot.message_handler(commands=['countries'])
def show_countries(message):
    text = "🌍 کشورها:\n\n"
    for k, v in COUNTRIES.items():
        text += f"🏳 {k} → {v}\n"

    text += "\n❗ انتخاب کشور فقط توسط ادمین است."
    bot.send_message(message.chat.id, text)

# ================== انتخاب کشور (ادمین) ==================
@bot.message_handler(commands=['setcountry'])
def set_country(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, user_id, country = message.text.split(maxsplit=2)
        user_id = int(user_id)

        if country not in COUNTRIES:
            bot.send_message(message.chat.id, "❌ کشور نامعتبر است")
            return

        c.execute("UPDATE users SET country=? WHERE user_id=?", (country, user_id))
        conn.commit()

        bot.send_message(message.chat.id, "✅ کشور با موفقیت ثبت شد")

    except:
        bot.send_message(
            message.chat.id,
            "فرمت:\n/setcountry USER_ID نام_کشور"
        )

# ================== آموزش اژدها ==================
@bot.message_handler(commands=['train_dragon'])
def train_dragon(message):
    user_id = message.from_user.id
    c.execute("SELECT gold,food,wood,dragons FROM users WHERE user_id=?", (user_id,))
    u = c.fetchone()

    if not u:
        return

    gold, food, wood, dragons = u

    if gold >= 3000 and food >= 2000 and wood >= 1500:
        c.execute("""
        UPDATE users SET
        gold=gold-3000,
        food=food-2000,
        wood=wood-1500,
        dragons=dragons+1
        WHERE user_id=?
        """, (user_id,))
        conn.commit()

        bot.send_message(message.chat.id, "🐉 اژدها با موفقیت آموزش داده شد!")
    else:
        bot.send_message(message.chat.id, "❌ منابع کافی نیست")

# ================== حمله PVP ==================
@bot.message_handler(commands=['attack'])
def attack(message):
    user_id = message.from_user.id

    try:
        _, target_id = message.text.split()
        target_id = int(target_id)
    except:
        bot.send_message(message.chat.id, "فرمت:\n/attack USER_ID")
        return

    c.execute("SELECT soldiers,dragons FROM users WHERE user_id=?", (user_id,))
    a = c.fetchone()
    c.execute("SELECT soldiers,dragons FROM users WHERE user_id=?", (target_id,))
    d = c.fetchone()

    if not a or not d:
        bot.send_message(message.chat.id, "❌ بازیکن پیدا نشد")
        return

    power_a = a[0] + a[1]*50
    power_d = d[0] + d[1]*50

    if power_a > power_d:
        gold_win = random.randint(100,300)
        c.execute("UPDATE users SET gold=gold+? WHERE user_id=?", (gold_win, user_id))
        conn.commit()
        bot.send_message(message.chat.id, f"🔥 پیروزی! {gold_win} طلا غارت شد")
    else:
        bot.send_message(message.chat.id, "❌ حمله شکست خورد")

# ================== اجرا ==================
print("Bot is running...")
bot.infinity_polling()
