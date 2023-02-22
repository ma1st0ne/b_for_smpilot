import sqlite3

db = sqlite3.connect('sympathy.db', check_same_thread=False)


def show_auth_codes():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM auth_codes')
    rows = cursor.fetchall()
    for row in rows:
        print(row[0])
    return 1


if __name__ == '__main__':
    show_auth_codes()
