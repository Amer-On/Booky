import sqlite3
import csv

conn = sqlite3.connect(r'databases/users.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
   user_id INT PRIMARY KEY,
   user_name TEXT,
   phone TEXT,
   city TEXT,
   email TEXT);
""")
conn.commit()


class User:
    def __init__(self, user_name, phone, city, email):
        self.name = user_name
        self.phone = phone
        self.city = city
        self.email = email

    def __str__(self):
        return f"""Имя пользователя: <em>{self.name}</em>
Номер телефона: <em>{self.phone}</em>
Город: <em>{self.city}</em>
Электронная почта: <em>{self.email}</em>"""

    def __repr__(self):
        return str(self)


def is_user_in(user_id: int):
    with conn:
        users = cur.execute("SELECT user_id FROM users where user_id=?;",
                            (user_id,))
        return bool(users.fetchall())


def get_user_city(user_id: int):
    with conn:
        city = cur.execute("SELECT city from users where user_id=?;",
                           (user_id,)).fetchall()
    return city[0][0]


def set_city(user_id: int, city: str):
    user = cur.execute("SELECT * FROM users WHERE user_id=?;",
                        (user_id,)).fetchall()[0]

    with conn:
        cur.execute("DELETE FROM users where user_id=?;",
                    (user_id, ))

    user = list(user)
    user[3] = city
    save_user(*user)


def get_user(user_id: int):
    users = cur.execute("SELECT * FROM users WHERE user_id=?;",
                        (user_id, )).fetchall()

    return User(*users[0][1:])


def get_all_users():
    cur.execute("SELECT * FROM users;")
    return cur.fetchall()


def save_user(user_id: int, user_name: str, phone: str, city: str, email: str):
    with conn:
        cur.execute("insert into users (user_id, user_name, phone, city, email) values (?, ?, ?, ?, ?);",
                    (user_id, user_name, phone, city, email,))
    conn.commit()


def clear_users_db():
    _delete_table('users')


def _delete_table(table_name: str):
    with conn:
        cur.execute(f'delete from {table_name};')
    conn.commit()


def db_to_csv():
    """ Mainly to check the data in database to confirm everything works correctly"""
    with conn:
        data = cur.execute("select * from users;")

        with open("databases/users.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'user_name', 'phone', 'city', 'email'])
            writer.writerows(data)


if __name__ == "__main__":
    pass
