import sqlite3 

def init():
    conn= sqlite3.connect('db.db')
    # drop the entire db
    conn.execute('DROP TABLE IF EXISTS pet_images')
    conn.execute('DROP TABLE IF EXISTS interested_users')
    conn.execute('DROP TABLE IF EXISTS pets')
    conn.execute('DROP TABLE IF EXISTS users')

    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, password TEXT, contact INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS interested_users (id INTEGER PRIMARY KEY, users_id INTEGER REFERENCES users(id), pet_id INTEGER REFERENCES pets(id))')
    conn.execute('CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY, name TEXT, sex TEXT, age INTEGER, fee INTEGER, writeup TEXT, type TEXT, owner_id INTEGER REFERENCES users(id))')
    conn.execute('CREATE TABLE IF NOT EXISTS pet_images (id INTEGER PRIMARY KEY, pet_id INTEGER REFERENCES pets(id), image1 BLOB, image2 BLOB, image3 BLOB)')

    conn.commit()
    # show tables in db
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    conn.close()
