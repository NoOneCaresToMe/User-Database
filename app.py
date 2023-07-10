from flask import Flask, render_template, request, redirect, g, session
import sqlite3

app = Flask(__name__)

# Configuration
DATABASE = 'customer.db'
SECRET_KEY = 'secret_key'

app.config.from_object(__name__)

# Create a connection to the SQLite database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

# Create the customer table if it doesn't exist
def init_db():
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS customers 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      phone TEXT,
                      address TEXT,
                      remark TEXT)''')
        db.commit()

def get_latest_customer():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM customers ORDER BY id DESC LIMIT 1")
    latest_customer = c.fetchone()
    conn.close()
    return latest_customer

def get_previous_customer():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM customers ORDER BY id DESC LIMIT 2")
    customers = c.fetchall()
    conn.close()
    if len(customers) >= 2:
        return customers[1]
    else:
        return None
    
@app.route('/')
def index():
    if 'username' in session:
        latest_customer = get_latest_customer()
        previous_customer = get_previous_customer()
        return render_template('index.html', latest_customer=latest_customer, previous_customer=previous_customer)
    else:
        return redirect('/login')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        remark = request.form['remark']

        # Insert the customer data into the database
        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO customers (name, phone, address, remark) VALUES (?, ?, ?, ?)",
                  (name, phone, address, remark))
        db.commit()

        return redirect('/')

    return render_template('register.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        customer_id = request.form['customer_id']

        # Fetch customer details from the database
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
        customer = c.fetchone()

        if customer:
            return render_template('edit.html', customer=customer)
        else:
            return render_template('edit.html', error="Customer not found")

    return render_template('edit.html')

@app.route('/update', methods=['POST'])
def update():
    if 'username' not in session:
        return redirect('/login')

    customer_id = request.form['customer_id']
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    remark = request.form['remark']

    # Update the customer data in the database
    db = get_db()
    c = db.cursor()
    c.execute("UPDATE customers SET name=?, phone=?, address=?, remark=? WHERE id=?",
              (name, phone, address, remark, customer_id))
    db.commit()

    return redirect('/')
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        customer_id = request.form['customer_id']

        # Delete the customer from the database
        db = get_db()
        c = db.cursor()
        c.execute("DELETE FROM customers WHERE id=?", (customer_id,))
        db.commit()

        return redirect('/')

    return render_template('delete.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password are valid
        if username == 'admin' and password == 'admin':
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.secret_key = app.config['SECRET_KEY']
    init_db()
    app.run(debug=True)
