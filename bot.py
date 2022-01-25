import telebot
import config
import sqlite3

bot = telebot.TeleBot(config.token, parse_mode=None)

help_message = 'Как пользоваться:\n\n' \
                   'Чтобы получить данные записи, отправь сообщение следующего формата:\n' \
                   '? запрос\n' \
                   'Пример: ? авито\n' \
                   'Регистр значения не имеет (можно использовать заглавные и строчные буквы, без разницы)\n\n' \
                   'Чтобы сохранить данные для сайта, отправь сообщение следующего формата:\n' \
                   '! название, логин, пароль\n' \
                   'Пример: ! авито, someLogin, kurva666\n' \
                   'В наименовании регистр не важен. Важно отделять запятыми наименование, логин и пароль.'


@bot.message_handler(commands=['start', 'help', 'как'])
def send_welcome(message):
    bot.send_message(message.chat.id, help_message)


@bot.message_handler(func=lambda message: message.chat.id not in config.user_ids_with_access)
def some(message):
    img = open('./who are you.jpg', 'rb')
    bot.send_photo(message.chat.id, img)


@bot.message_handler(content_types=['text'])
def main(message):
    """
    Основная функция взаимодействия с пользователем. Получает сообщение и на основе первого символа -
    либо, если символ '!', разбирает сообщение на составляющие и сохраняет данные в БД,
    либо, если символ '?', ищет все вхождения в БД и выводит их в ответном сообщении.
    """
    conn = sqlite3.connect('passwords.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS passwords(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       site_name TEXT,
       login TEXT,
       password TEXT);
    """)
    conn.commit()
    if message.text.strip()[0] == '!':
        record = message.text[1:].strip().split(',')
        site_name = record[0].strip().lower()
        login = record[1].strip()
        password = record[2].strip()
        cur.execute(f"INSERT INTO passwords(site_name, login, password) VALUES('{site_name}', '{login}', '{password}');")
        conn.commit()
        bot.send_message(message.chat.id, f'Добавлена запись для сайта {site_name}, логин: {login}, пароль: {password}')
    elif message.text.strip()[0] == '?':
        request_name = message.text[1:].strip().lower()
        cur.execute(f"SELECT * FROM passwords WHERE site_name LIKE '%{request_name}%';")
        results = cur.fetchall()
        if len(results):
            result_message = f'По запросу "{request_name}" найдены следующие записи:\n'
            for result in results:
                result_message += f'{result[1]}    {result[2]}    {result[3]}\n'
        else:
            result_message = f'По запросу "{request_name}" записей не найдено 😔'
        bot.send_message(message.chat.id, result_message)
    elif message.text:
        bot.send_message(message.chat.id, 'Шо ты от меня хочешь, не пойму? Чтобы посмотреть, как правильно '
                                          'составить запрос, жми на ссылку /help')


bot.infinity_polling(interval=0, timeout=20)
