import os
import telebot
from telebot import types
import openai
import sqlite3
from dotenv import load_dotenv
from threading import Thread
import datetime

load_dotenv()

# Подключение к API
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
DB_PATH = os.getenv("DB_PATH", "tg_base_psiho.db")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Не найден TELEGRAM_BOT_TOKEN в .env")
if not OPENAI_API_KEY:
    raise ValueError("Не найден OPENAI_API_KEY в .env")
if not CHANNEL_USERNAME:
    raise ValueError("Не найден CHANNEL_USERNAME в .env")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY
channel_username = CHANNEL_USERNAME

 #Создание SQL tableя
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

with open('start.txt', encoding='utf-8') as file_start:
    start_message = file_start.read()

query = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    call_item INTEGER NOT NULL DEFAULT 3,
    data DATE DEFAULT CURRENT_DATE,
    colih INTEGER NOT NULL DEFAULT 1, 
    tip VARCHAR,
    dialog TEXT
)
"""

cursor.execute(query)
conn.commit()
def clear_history(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET dialog = NULL WHERE user_id=?", [user_id])
        conn.commit()
        cursor.execute("UPDATE users SET colih = 1 WHERE user_id=?", [user_id])
        conn.commit()

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
#Проверка на админа
def is_admin(user_id):
    response = bot.get_chat_member(channel_username, user_id)
    if response.status == 'administrator':
        return True
    else:
        return False

#Проверка на подписку
def check_subscription(user_id):
    response = bot.get_chat_member(channel_username, user_id)
    if response.status == 'member' or response.status == 'administrator' or response.status == 'creator':

        return True
    else:
        return False

#добовление подписки(plus)
def extend_data(message,rit):
    if is_admin(message.from_user.id):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            command_parts = message.text.split()
            if len(command_parts) != 3:
                bot.send_message(message.chat.id, "Неверный формат команды.")
                return

            user_id = int(command_parts[1])
            data_plus = int(command_parts[2])
            if rit == 0:
                cursor.execute("SELECT date('now')")
                current_data = cursor.fetchone()[0]
            if rit == 1:
                cursor.execute("SELECT data FROM users WHERE user_id = ?", [user_id])
                current_data = cursor.fetchone()[0]
            current_date = datetime.datetime.strptime(current_data, "%Y-%m-%d").date()
            new_data = (current_date + datetime.timedelta(days=30 * data_plus)).strftime("%Y-%m-%d")

            cursor.execute("UPDATE users SET data = ? WHERE user_id = ?", [new_data, user_id])
            conn.commit()

            bot.send_message(message.chat.id,f"Дата для пользователя {user_id} успешно увеличена на {data_plus} месяцев.")
            cursor.close()
            conn.close()
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при увеличении data: {str(e)}")

def start_dialog(message):
    # начинаем диалог
    user_id = message.from_user.id
    if check_subscription(user_id):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT call_item FROM users WHERE user_id=?", [user_id])
            result = cursor.fetchone()
            cursor.execute("SELECT data FROM users WHERE user_id = ?", [user_id])
            data_id = cursor.fetchone()
            data_id = datetime.datetime.strptime(data_id[0], "%Y-%m-%d").date()
            current_date = datetime.date.today()

            if result[0] != 0 or data_id >= current_date and isinstance(message.text, str):
                bot.send_message(message.chat.id, "ℹ️Режим диалога включенℹ️")
                bot.register_next_step_handler(message, gpt)


            elif isinstance(message.text, str) != True:
                bot.send_message(message.chat.id, "Извините, запрос не удалось обработать")

            else:
                clear_history(user_id)
                bot.send_message(message.chat.id, "ℹ️У вас закончились запросыℹ️")
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)

    else:
        markup1 = types.InlineKeyboardMarkup()
        check = types.InlineKeyboardButton(text="Проверить подписку", callback_data="check")
        markup1.add(check)
        bot.send_message(message.chat.id,f"Для использования бота вам необходимо подписаться на канал: {channel_username}.\nВ данной группе будет выкладываться актуальная информация о нашем проекте.",reply_markup=markup1)

def gpt(message):
    user_id = message.from_user.id
    if check_subscription(user_id):
        if message.text == "/end":
            clear_history(user_id)
            bot.send_message(message.chat.id, "ℹ️Режим диалога выключенℹ️")
        elif isinstance(message.text, str):
            try:
                bot.send_message(message.chat.id, "🕰️⏰🕙⏱️⏳...")
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                question = message.text
                cursor.execute("SELECT dialog FROM users WHERE user_id=?", [user_id])
                dialog = cursor.fetchone()
                cursor.execute("SELECT tip FROM users WHERE user_id = ?",[user_id])
                tip_chel = cursor.fetchone()
                cursor.execute("SELECT colih FROM users WHERE user_id = ?",[user_id])
                colih: object = cursor.fetchone()[0]


                if dialog[0] is None:
                    dialog_text = f" Здравствуй, я хочу, чтобы ты выступил в роли моего виртуального зеркального отражения с типом личности {tip_chel}. Пожалуйста, отвечай на мои вопросы и вступай в разговор, как если бы ты был мной, с теми же ценностями, интересами и предпочтениями.Так же не упоминай в своих сообщениях про мой тип личности. Давай начнем.\n" + question + "\n"
                else:
                    dialog_text = dialog[0] + question + "\n"


                # Генерация ответа с помощью GPT
                answer = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-0301",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": dialog_text}
                    ]
                )

                # Сохранение ответа в базе данных


                cursor.execute("SELECT call_item FROM users WHERE user_id=?", [user_id])
                result = cursor.fetchone()

                cursor.execute("SELECT data FROM users WHERE user_id = ?", [user_id])
                data_id = cursor.fetchone()

                data_id = datetime.datetime.strptime(data_id[0], "%Y-%m-%d").date()
                current_date = datetime.date.today()

                if data_id >= current_date and isinstance(message.text, str) and colih <= 20:

                    try:

                        bot.send_message(message.chat.id, answer.choices[0].message.content)
                        bot.register_next_step_handler(message, gpt)
                        cursor.execute("UPDATE users SET colih = colih + 1 WHERE user_id=?", [user_id])
                        conn.commit()
                        cursor.execute("SELECT dialog FROM users WHERE user_id=?", [user_id])
                        dialog = cursor.fetchone()
                        if dialog[0] is None:
                            dialog_text = question + "\n" + answer.choices[0].message.content + "\n"
                        else:
                            dialog_text = dialog[0] + question + "\n" + answer.choices[0].message.content + "\n"
                        cursor.execute("UPDATE users SET dialog = ? WHERE user_id=?", [dialog_text, user_id])
                        conn.commit()
                        bot.send_message(message.chat.id,f"Запрос: {colih} из 20")


                    except:
                        bot.send_message(message.chat.id, "Извините, запрос не удалось обработать")

                elif result[0] != 0 and isinstance(message.text, str) and colih <= 20:
                    cursor.execute("UPDATE users SET call_item = call_item - 1 WHERE user_id=?", [user_id])
                    conn.commit()

                    try:

                        bot.send_message(message.chat.id, answer.choices[0].message.content)
                        bot.register_next_step_handler(message, gpt)
                        cursor.execute("SELECT dialog FROM users WHERE user_id=?", [user_id])
                        dialog = cursor.fetchone()
                        cursor.execute("UPDATE users SET colih = colih + 1 WHERE user_id=?", [user_id])
                        conn.commit()

                        if dialog[0] is None:
                            dialog_text = question + "\n" + answer.choices[0].message.content + "\n"
                        else:
                            dialog_text = dialog[0] + question + "\n" + answer.choices[0].message.content + "\n"
                        cursor.execute("UPDATE users SET dialog = ? WHERE user_id=?", [dialog_text, user_id])
                        conn.commit()
                        bot.send_message(message.chat.id, f"Запрос: {colih} из 20")

                    except:
                        bot.send_message(message.chat.id, "Извините, запрос не удалось обработать")
                elif colih > 20:
                    clear_history(user_id)
                    bot.send_message(message.chat.id,"ℹ️Превышен лимит запросов, диалог будет остановлен. ℹ️\nВы можете начать диалог заново, для этого нажмите команду /begin")

                elif result[0] == 0 and isinstance(message.text, str):
                    clear_history(user_id)
                    bot.send_message(message.chat.id, "ℹ️У вас закончились запросыℹ️")

                elif data_id < current_date and isinstance(message.text, str):
                    clear_history(user_id)
                    bot.send_message(message.chat.id, "ℹ️У вас закончилась подпискаℹ️")
                elif isinstance(message.text, str) != True:
                    clear_history(user_id)
                    bot.send_message(message.chat.id, "Извините, запрос не удалось обработать")

                cursor.close()
                conn.close()
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, "Извините, бот временно не доступен")


    else:
        markup1 = types.InlineKeyboardMarkup()
        check = types.InlineKeyboardButton(text="Проверить подписку", callback_data="check")
        markup1.add(check)
        bot.send_message(message.chat.id,f"Для использования бота вам необходимо подписаться на канал: {channel_username}.\nВ данной группе будет выкладываться актуальная информация о нашем проекте.",reply_markup=markup1)

#Обработка команды /start
@bot.message_handler(commands=['start','info'])
def start(message):
    try:
        user_id = message.from_user.id
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        #Проверка наличия id пользователя в таблице
        cursor.execute("SELECT * FROM users WHERE user_id=?", [user_id])
        existing_user = cursor.fetchone()
        if existing_user:
            pass
        else:
            # Добавление нового пользователя в таблицу
            cursor.execute("INSERT INTO users(user_id) VALUES (?)", [user_id])
            current_date = datetime.date.today()
            previous_date = current_date - datetime.timedelta(days=1)
            previous_date_str = previous_date.strftime("%Y-%m-%d")
            cursor.execute("UPDATE users SET data = ? WHERE user_id=?", [previous_date_str,user_id])
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
    if check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        website_man = types.InlineKeyboardButton(text="Тест для Мужчин",url="https://happypeople.blog/test/test-na-tip-lichnosti-po-tipologii-majers-briggs-mvti-dlya-muzhchin/")
        website_girl = types.InlineKeyboardButton(text="Тест для Женщин",url="https://happypeople.blog/test/test-na-tip-lichnosti-po-tipologii-majers-briggs-mvti-dlya-zhenshhin/")
        markup.add(website_man,website_girl)

        bot.send_message(message.chat.id,start_message,reply_markup=markup)

    else:
        markup1 = types.InlineKeyboardMarkup()
        check = types.InlineKeyboardButton(text = "Проверить подписку", callback_data= "check")
        markup1.add(check)
        bot.send_message(message.chat.id, f"Для использования бота вам необходимо подписаться на канал: {channel_username}.\nВ данной группе будет выкладываться актуальная информация о нашем проекте.",reply_markup=markup1)

@bot.message_handler(commands=['begin'])
def start_dialogue(message):
    user_id = message.from_user.id
    if check_subscription(user_id):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT tip FROM users WHERE user_id = ?", [user_id])
            tip_chel = cursor.fetchone()[0]
            if not bot.get_chat_member(message.chat.id, user_id).status == "member":
                bot.send_message(message.chat.id, "ℹ️Режим диалога включенℹ️")
            elif bot.get_chat_member(message.chat.id, message.from_user.id).status == "member":
                cursor.execute("SELECT call_item FROM users WHERE user_id=?", [user_id])
                result = cursor.fetchone()
                cursor.execute("SELECT data FROM users WHERE user_id = ?",[user_id])
                data_id = cursor.fetchone()
                data_id = datetime.datetime.strptime(data_id[0], "%Y-%m-%d").date()
                current_date = datetime.date.today()

                if result[0] != 0 or data_id >= current_date and isinstance(message.text, str):
                    if tip_chel is None:
                        bot.send_message(message.chat.id,"Для начала диалога необходимо установить свой тип личности.\nВы можете это сделать c помощью команды /profile")
                    else:
                        clear_history(user_id)
                        start_dialog(message)

                elif isinstance(message.text, str) != True:
                    clear_history(user_id)
                    bot.send_message(message.chat.id, "Извините, запрос не удалось обработать")
                else:
                    clear_history(user_id)
                    bot.send_message(message.chat.id, "ℹ️У вас закончились запросыℹ️")
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)

    else:
        markup1 = types.InlineKeyboardMarkup()
        check = types.InlineKeyboardButton(text="Проверить подписку", callback_data="check")
        markup1.add(check)
        bot.send_message(message.chat.id,f"Для использования бота вам необходимо подписаться на канал: {channel_username}.\nВ данной группе будет выкладываться актуальная информация о нашем проекте.",reply_markup=markup1)

@bot.message_handler(commands=['end'])
def end_dialogue(message):
    user_id = message.from_user.id
    if check_subscription(user_id):

        if bot.get_chat_member(message.chat.id, message.from_user.id).status == "member":
            clear_history(user_id)
            bot.send_message(message.chat.id, "ℹ️Режим диалога (по-прежнему) выключенℹ️")
        else:
            clear_history(user_id)
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            bot.send_message(message.chat.id, "ℹ️Режим диалога выключенℹ️")
    else:
        markup1 = types.InlineKeyboardMarkup()
        check = types.InlineKeyboardButton(text="Проверить подписку", callback_data="check")
        markup1.add(check)
        bot.send_message(message.chat.id,f"Для использования бота вам необходимо подписаться на канал: {channel_username}.\nВ данной группе будет выкладываться актуальная информация о нашем проекте.",reply_markup=markup1)

@bot.message_handler(commands=['profile'])
def profile(message):
    user_id = message.from_user.id

    if check_subscription(user_id):
        try:
            markup = types.InlineKeyboardMarkup()
            edit_tip = types.InlineKeyboardButton(text = "Изменить тип личности", callback_data= "tip")
            pokupka = types.InlineKeyboardButton(text = "Перейти к товарам",callback_data="pokupka")
            markup.add(edit_tip)

            user_id = message.from_user.id
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Получение количества статусов для данного профиля
            cursor.execute("SELECT call_item FROM users WHERE user_id=?", [user_id])
            status_count = cursor.fetchone()[0]
            first_name = message.from_user.first_name
            cursor.execute("SELECT data FROM users WHERE user_id = ?", [user_id])
            data_id = cursor.fetchone()
            data_id = datetime.datetime.strptime(data_id[0], "%Y-%m-%d").date()
            current_date = datetime.date.today()
            cursor.execute("SELECT tip FROM users WHERE user_id = ?", [user_id])
            tip_test = cursor.fetchone()
            if tip_test[0] is None:
                tip_test = "Неопределен"
            else:
                tip_test = tip_test[0]
            if is_admin(user_id):
                bot.send_message(message.chat.id, f"Профиль админа: {first_name}\nТип личности: {tip_test}\nАйди пользователя: {user_id}\n\n Админ панель\n\n1) Увеличение подписки на месяц.\nПример: /1010 user_id data_plus\n\n2) Добавление к подписки месяц.\nПример: /1011 user_id data_plus\n\n3) Просмотр количества пользователей: /1020\n\n4) Добавление бесплатных запросов.\nПример: /1012 user_id free_tik\n\n5)Получить файл базы данных: /1030",reply_markup= markup)

            elif data_id >= current_date:
                bot.send_message(message.chat.id,f"Профиль: {first_name}\nТип личности: {tip_test}\nАйди пользователя: {user_id}\nПодписка до: {data_id}",reply_markup= markup)

            else:
                bot.send_message(message.chat.id, f"Профиль: {first_name}\nТип личности: {tip_test}\nАйди пользователя: {user_id}\nКоличество бесплатных запросов: {status_count}",reply_markup= markup)
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)

    else:
        markup1 = types.InlineKeyboardMarkup()
        check = types.InlineKeyboardButton(text="Проверить подписку", callback_data="check")
        markup1.add(check)
        bot.send_message(message.chat.id,f"Для использования бота вам необходимо подписаться на канал: {channel_username}.\nВ данной группе будет выкладываться актуальная информация о нашем проекте.",reply_markup=markup1)

@bot.message_handler(commands=["1010"])
def extend_data_0(message):
    extend_data(message,0)
@bot.message_handler(commands=["1011"])
def extend_data_1(message):
    extend_data(message,1)
@bot.message_handler(commands=["1012"])
def extend_tik(message):
    if is_admin(message.from_user.id):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            command_parts = message.text.split()
            if len(command_parts) != 3:
                bot.send_message(message.chat.id, "Неверный формат команды.")
                return
            user_id = int(command_parts[1])
            free_tik = int(command_parts[2])
            cursor.execute("UPDATE users SET call_item = call_item + ? WHERE user_id = ?",[free_tik,user_id])
            conn.commit()
            bot.send_message(message.chat.id,f"Бесплатные запросы для пользователя {user_id} успешно увеличены на {free_tik}.")
            cursor.close()
            conn.close()
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка запроса: {str(e)}")

@bot.message_handler(commands="1020")
def num_people(message):
    if is_admin(message.from_user.id):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(id) FROM users")
            num_people_all = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users WHERE data > DATE('now')")
            num_people_price = cursor.fetchone()[0]

            bot.send_message(message.chat.id,f"В данный момент зарегестрированных пользователей: {num_people_all}\nВ данный момент платных пользователей: {num_people_price}")
            cursor.close()
            conn.close()
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка запроса: {str(e)}")

@bot.message_handler(commands="1030")
def send_file(message):
    if is_admin(message.from_user.id):
        try:
            # Путь к базе данных
            db_file = DB_PATH

            # Отправка файла в чат
            with open(db_file, 'rb') as file:
                bot.send_document(message.chat.id, file)

        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка запроса: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "tip":
        ISTP = types.InlineKeyboardButton("ISTP", callback_data='ISTP')
        ISFP = types.InlineKeyboardButton("ISFP", callback_data='ISFP')
        INFP = types.InlineKeyboardButton("INFP", callback_data='INFP')
        INTP = types.InlineKeyboardButton("INTP", callback_data='INTP')
        ESTP = types.InlineKeyboardButton("ESTP", callback_data='ESTP')
        ESFP = types.InlineKeyboardButton("ESFP", callback_data='ESFP')
        ENFP = types.InlineKeyboardButton("ENFP", callback_data='ENFP')
        ENTP = types.InlineKeyboardButton("ENTP", callback_data='ENTP')
        ISTJ = types.InlineKeyboardButton("ISTJ", callback_data='ISTJ')
        ISFJ = types.InlineKeyboardButton("ISFJ", callback_data='ISFJ')
        INFJ = types.InlineKeyboardButton("INFJ", callback_data='INFJ')
        INTJ = types.InlineKeyboardButton("INTJ", callback_data='INTJ')
        ESTJ = types.InlineKeyboardButton("ESTJ", callback_data='ESTJ')
        ESFJ = types.InlineKeyboardButton("ESFJ", callback_data='ESFJ')
        ENFJ = types.InlineKeyboardButton("ENFJ", callback_data='ENFJ')
        ENTJ = types.InlineKeyboardButton("ENTJ", callback_data='ENTJ')
        markup2 = types.InlineKeyboardMarkup(row_width=4)
        markup2.add(ISTP, ISFP, INFP, INTP, ESTP, ESFP, ENFP, ENTP, ISTJ, ISFJ, INFJ, INTJ, ESTJ, ESFJ, ENFJ, ENTJ)
        bot.send_message(call.message.chat.id, "Выбери свой тип личности:", reply_markup=markup2)
    elif call.data == "pokupka":
        markup3 = types.InlineKeyboardMarkup()
        mounth1 = types.InlineKeyboardButton("1 Месяц подписки",callback_data="1_mounth")
        markup3.add(mounth1)
        bot.send_message(call.message.chat.id,"Вы можете купить ниже перечисленные товары:\n - Подписка на месяц - 350 рублей",reply_markup=markup3)

    elif call.data != "check":
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET tip = ? WHERE user_id = ?", [call.data, call.message.chat.id])
            conn.commit()
            cursor.close()
            conn.close()
            bot.send_message(call.message.chat.id, f"Тип личности успешно изменен на {call.data}")
        except Exception as e:
            print(e)

    if call.data == "check":
        if check_subscription(call.message.chat.id):
            markup = types.InlineKeyboardMarkup()
            website_man = types.InlineKeyboardButton(text="Тест для Мужчин",url="https://happypeople.blog/test/test-na-tip-lichnosti-po-tipologii-majers-briggs-mvti-dlya-muzhchin/")
            website_girl = types.InlineKeyboardButton(text="Тест для Женщин",url="https://happypeople.blog/test/test-na-tip-lichnosti-po-tipologii-majers-briggs-mvti-dlya-zhenshhin/")
            markup.add(website_man, website_girl)
            bot.send_message(call.message.chat.id,"Подписка прошла успешна!")

            bot.send_message(call.message.chat.id, start_message, reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id,"Вы еше не подписались.")

print("run")
# Запуск бота в отдельном потоке
bot_thread = Thread(target=bot.infinity_polling)
bot_thread.start()