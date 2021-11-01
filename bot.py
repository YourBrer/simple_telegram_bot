import telebot
import config
import sqlite3

bot = telebot.TeleBot(config.token, parse_mode=None)

template_message = 'Как пользоваться:\n\n' \
                   'Чтобы получить данные записи, отправь сообщение следующего формата:\n' \
                   '? имя_сайта\n' \
                   'Пример: ? авито\n' \
                   'Регистр значения не имеет (можно использовать заглавные и строчные буквы, без разницы)\n\n' \
                   'Чтобы сохранить данные для сайта, отправь сообщение следующего формата:\n' \
                   '! название_сайта, логин, пароль\n' \
                   'Пример: ! авито, emma mirn, kurica666\n' \
                   'В имени сайта регистр не важен. Важно отделять запятыми имя сайта, логин и пароль.'


@bot.message_handler(commands=['start', 'help', 'как'])
def send_welcome(message):
    bot.send_message(message.chat.id, template_message)


@bot.message_handler(content_types=['text'])
def main(message):
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
            site_name = message.text[1:].strip().lower()
            cur.execute(f"SELECT * FROM passwords WHERE site_name='{site_name}' ;")
            results = cur.fetchall()
            if len(results):
                result_message = f'Для сайта "{site_name}" найдено:\n'
                for result in results:
                    result_message += f'логин: {result[2]}, пароль: {result[3]}\n'
            else:
                result_message = f'Для сайта "{site_name}" записей не найдено 😔'
            bot.send_message(message.chat.id, result_message)
        else:
            bot.send_message(message.chat.id, 'Шо ты от меня хочешь, не пойму? Чтобы посмотреть, как правильно '
                                              'составить запрос, жми на ссылку /help')


bot.polling(none_stop=True)
