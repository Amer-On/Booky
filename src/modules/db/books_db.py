import sqlite3
import csv

conn = sqlite3.connect(r'databases/books.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS books(
    title TEXT,
    author TEXT,
    rating TEXT,
    description TEXT,
    city TEXT,
    owner INT
    );
""")
conn.commit()


def add_book(title: str, author: str, rating: str, description: str, city: str, owner_id: int):
    with conn:
        cur.execute("insert into books (title, author, rating, description, city, owner) values (?, ?, ?, ?, ?, ?);",
                    (title, author, rating, description, city, owner_id))


def get_all_books():
    cur.execute("SELECT * FROM books;")
    return cur.fetchall()


def get_books_from_city(city: str):
    with conn:
        books = cur.execute("SELECT * FROM books where city=?;",
                        (city, )).fetchall()
    return books


def clear_books_db():
    _delete_table('books')


def _delete_table(table_name: str):
    with conn:
        cur.execute(f'delete from {table_name};')
    conn.commit()


def db_to_csv():
    """ Mainly to check the data in database to confirm everything works correctly"""
    with conn:
        data = cur.execute("select * from books;")

        with open("databases/books.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['title', 'author', 'description', 'owner'])
            writer.writerows(data)


if __name__ == "__main__":
    pass