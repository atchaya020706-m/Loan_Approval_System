import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# Delete old loans table (only for development)
cursor.execute("DROP TABLE IF EXISTS loans")

# Create new loans table
cursor.execute("""
CREATE TABLE loans(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    loan_type TEXT,

    purpose TEXT,

    age INTEGER,

    income REAL,

    loan_amount REAL,

    credit_score INTEGER,

    result TEXT

)
""")

conn.commit()

conn.close()

print("Loan table created successfully")