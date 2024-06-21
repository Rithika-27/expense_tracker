from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['expense_tracker']
users_collection = db['users']
expenses_collection = db['expenses']

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if users_collection.find_one({'email': email}):
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        # Hash the password and store user details
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })
        return jsonify({'success': True, 'message': 'Registration successful'})

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = users_collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            flash('Login successful!', 'success')
            session['user_id'] = str(user['_id'])  # Store user ID in session
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        
        expenses_collection.insert_one({
            'user_id': ObjectId(user_id),
            'description': description,
            'amount': amount,
            'category': category
        })
        flash('Expense added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    user_expenses = list(expenses_collection.find({'user_id': ObjectId(user_id)}))
    return render_template('dashboard.html', expenses=user_expenses)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
