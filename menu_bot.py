import logging
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔑 Встав свій токен бота
TELEGRAM_TOKEN = "7571362294:AAEaUrcXZoH083xchA4qoGZAbwL0ASVQ7r4"

# 🔗 Авторизація Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("poetic-archive-464217-a5-1e1022fa02a4.json", SCOPE)
client = gspread.authorize(CREDS)

# 📄 Назва таблиці (та, яку ти створила)
sheet = client.open("меню_бот_без_цен").sheet1
data = sheet.get_all_records()

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 🔹 Отримуємо категорії
def get_categories():
    return sorted(set(row["Категория"] for row in data))

# 🔹 Страви по категорії
def get_dishes(category):
    return [row for row in data if row["Категория"] == category]

@bot.message_handler(commands=["start"])
def start(message):
    markup = InlineKeyboardMarkup()
    for category in get_categories():
        markup.add(InlineKeyboardButton(category, callback_data=f"cat_{category}"))
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def handle_category(call):
    category = call.data[4:]
    dishes = get_dishes(category)
    markup = InlineKeyboardMarkup()
    for row in dishes:
        markup.add(InlineKeyboardButton(row["Блюдо"], callback_data=f"dish_{row['Блюдо']}"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"📋 {category}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("dish_"))
def handle_dish(call):
    dish_name = call.data[5:]
    dish = next((row for row in data if row["Блюдо"] == dish_name), None)
    if dish:
        bot.send_photo(call.message.chat.id, photo=dish["Фото"], caption=f"🍽 <b>{dish_name}</b>", parse_mode="HTML")

print("🤖 Бот запущен!")
bot.polling(none_stop=True)
