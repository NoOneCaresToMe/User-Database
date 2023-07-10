import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

DATABASE = 'customer.db'

conn = sqlite3.connect(DATABASE)
c = conn.cursor()
# Create customers table if it does not exist
c.execute('''CREATE TABLE IF NOT EXISTS customer(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                address TEXT,
                remark TEXT
            )''')

conn.commit()
conn.close()

def get_latest_customer():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM customer ORDER BY id DESC LIMIT 1")
    latest_customer = c.fetchone()
    conn.close()
    return latest_customer

@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM customer")
    customers = c.fetchall()
    conn.close()

    latest_customer = get_latest_customer()

    return render_template('index.html', customers=customers, latest_customer=latest_customer)

if __name__ == '__main__':
    app.run()
