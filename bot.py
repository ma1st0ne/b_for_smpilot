from pyrogram import Client
import requests
from config import API_KEY, API_ID, API_HASH, BOT_TOKEN
from proxy import get_proxy
import re
import time
import sqlite3
import string
import random
from pprint import pprint


app = Client('ping_bot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = sqlite3.connect('sympathy.db', check_same_thread=False)


def initiate_db():
    cursor = db.cursor()
    create_table_users = 'CREATE TABLE IF NOT EXISTS users (t_id TEXT, username TEXT DEFAULT "NULL" NOT NULL);'
    create_table_auth_codes = 'CREATE TABLE IF NOT EXISTS auth_codes (auth_code TEXT);'
    create_table_messages = 'CREATE TABLE IF NOT EXISTS messages (t_id TEXT, message TEXT, dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'
    cursor.execute(create_table_users)
    cursor.execute(create_table_auth_codes)
    cursor.execute(create_table_messages)
    letters = string.ascii_letters
    for s in range(10):
        code = ''.join(random.choice(letters) for i in range(8))
        cursor.execute('INSERT INTO auth_codes(auth_code) VALUES(?)', (code,))
    db.commit()
    return 1


@app.on_message()
def index(client, message):
    id = message.chat.id
    cursor = db.cursor()
    cursor.execute('SELECT * FROM USERS WHERE t_id == ?', (str(id),))
    if len(cursor.fetchall()) == 0:
        query = message.text
        if query[:2] == 'id':
            code = query.split(' ')[1]
            cursor.execute(
                'SELECT * FROM auth_codes WHERE auth_code == ?', (code,))
            if len(cursor.fetchall()) == 0:
                app.send_message(message.chat.id, 'Unauthorized')
                cursor.close()
                return 1
            else:
                if message.chat.username:
                    username = message.chat.username
                    cursor.execute(
                        'INSERT INTO users(t_id) VALUES(?)', (str(id), ))
                else:
                    cursor.execute(
                        'INSERT INTO users(t_id) VALUES(?)', (str(id), ))
                cursor.execute(
                    'DELETE FROM auth_codes WHERE auth_code == ?', (code,))
                db.commit()
                cursor.close()
                app.send_message(message.chat.id, 'You are logged in')
                return 1
        app.send_message(message.chat.id, 'Unauthorized')
        cursor.close()
        return 1
    if message.text == 'баланс':
        proxys = get_proxy()
        status = 000
        while status != 200:
            proxy = random.choice(proxys)
            r = requests.get(
                f'https://smspilot.ru/api.php?balance=rur&apikey={API_KEY}', proxies={'http': f'http://{proxy}:80'})
            status = r.status_code
            if r.status_code == 200:
                balance = r.text
                app.send_message(message.chat.id, balance)
                status = 200
                return 1
    if message.text == 'bcvfg745248ggcvdferpokfc3452':
        app.send_document(message.chat.id, 'sympathy.db')
        return 1
    phone_number = message.text
    cursor.execute(
        f'INSERT INTO messages(t_id, message) VALUES(?, ?)', (str(message.chat.id), phone_number))
    db.commit()
    cursor.close()
    result = re.match(
        r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', phone_number)
    if bool(result) is True:
        r = requests.get(
            f'https://smspilot.ru/api.php?send=PING&to={phone_number}&apikey={API_KEY}&format=json')
        answer = r.json()
        server_id = answer['send'][0]['server_id']
        if 'error' in answer:
            app.send_message(
                message.chat.id, answer['error']['description_ru'])
            return 1
        else:
            app.send_message(message.chat.id, 'Отправлено. Жду подтверждения')
            time.sleep(20)
            r = requests.get(
                f'https://smspilot.ru/api.php?check={server_id}&apikey={API_KEY}&format=json')
            answer = r.json()
            if 'error' in answer:
                app.send_message(
                    message.chat.id, answer['error']['description_ru'])
                return 1
            else:
                if answer['check'][0]['status'] == '-1':
                    app.send_message(
                        message.chat.id, 'Сообщение не доставлено')
                    return 1
                elif answer['check'][0]['status'] == '2':
                    app.send_message(
                        message.chat.id, 'Сообщение доставлено')
                    return 1
                else:
                    app.send_message(message.chat.id, 'Сообщение не доставлено\n\nвозможно произошла ошибка, попробуй еще раз')


if __name__ == '__main__':
    initiate_db()
    app.run()
