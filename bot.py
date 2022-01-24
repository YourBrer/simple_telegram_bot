import telebot
import config
import sqlite3

# токен берется из файла конфигов, который я, само собой, заливать не буду))
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


@bot.message_handler(content_types=['text'])
def main(message):
    """
    Основная функция взаимодействия с пользователем. Получает сообщение и на основе первого символа
    либо, если символ '!', разбирает сообщение на составляющие и сохраняет данные в БД,
    либо, если символ '?', ищет все вхождения в БД и выводит их в ответном сообщении.
    """
    # т.к. изначально бот выполнял другие функции и был доступен большому количеству людей, чтобы не регистрировать
    # новый токен, я решил сделать проверку id отправителя сообщений и отвечать только избранным пользователям,
    # чьи id сохранил в файле конфига
    if message.from_user.id in config.user_ids_with_access:
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
                result_message = f'По запросу "{request_name}" найдено:\n'
                for result in results:
                    print(result)
                    result_message += f'наименование: {result[1]}, логин: {result[2]}, пароль: {result[3]}\n'
            else:
                result_message = f'По запросу "{request_name}" записей не найдено 😔'
            bot.send_message(message.chat.id, result_message)
        elif message.text:
            bot.send_message(message.chat.id, 'Шо ты от меня хочешь, не пойму? Чтобы посмотреть, как правильно '
                                              'составить запрос, жми на ссылку /help')


bot.infinity_polling(interval=0, timeout=20)
