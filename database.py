import sqlite3


def create_database():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()


    # User table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        email TEXT UNIQUE,

        password TEXT

    )
    """)



    # Loan application table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loan_applications(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        age INTEGER,

        income REAL,

        loan_amount REAL,

        credit_score INTEGER,

        status TEXT,

        FOREIGN KEY(user_id) REFERENCES users(id)

    )
    """)


    conn.commit()

    conn.close()



create_database()

print("Database Created Successfully")