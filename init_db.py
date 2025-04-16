import sqlite3

# Creation de la base de donnée
conn = sqlite3.connect('budget_app.db')
cursor = conn.cursor()

# Creation de table utilisateurs (users)
cursor.execute('''
               CREATE TABLE IF NOT EXISTS users(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT UNIQUE NOT NULL,
               email TEXT UNIQUE NOT NULL,
               password_hash TEXT NOT NULL
               )
''')

# Creation de table categories 
cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id))
''')

# Creation de table dépenses (expenses)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL,
               amount REAL NOT NULL,
               date TEXT NOT NULL,
               category_id INTEGER,
               user_id INTEGER,
               FOREIGN KEY(category_id) REFERENCES categories(id),
               FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

# Creation de table budgets
cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

# Creation de table budget_items (je vais modifier ça)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS budget_items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY(budget_id) REFERENCES budgets(id),
    FOREIGN KEY(category_id) REFERENCES categories(id)
    )
''')

conn.commit()
conn.close()