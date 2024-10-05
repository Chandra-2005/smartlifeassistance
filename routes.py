# routes.py

from flask import Blueprint, render_template, request, session, flash, redirect
from your_app_file import recommend_food, calculate_bmi, get_foods_to_avoid, hash_password, register_user, validate_user  # Import your functions
import sqlite3

# Create a Blueprint for your routes
main = Blueprint('main', __name__)

# Connect to the SQLite database (use a context manager if preferred)
def get_db_connection():
    conn = sqlite3.connect('nutrition.db')
    conn.row_factory = sqlite3.Row
    return conn

@main.route('/')
def index():
    if 'username' in session:
        recommended_foods = []
        bmi = None

        if request.method == 'POST':
            # Get user inputs and call recommend_food
            age = request.form['age']
            weight = request.form['weight']
            height = request.form['height']
            food_type = request.form['food_type']
            goal = request.form['goal']
            allergies = request.form['allergies']
            diseases = request.form['diseases']
            preference = request.form['preference']
            recommended_foods, bmi = recommend_food(age, weight, height, food_type, goal, allergies, diseases, preference)

        return render_template('index.html', recommended_foods=recommended_foods, bmi=bmi)

    return redirect('/login')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()

        if check_username_exists(username, cursor):
            if validate_user(username, password, cursor):
                session['username'] = username
                return redirect('/')
            else:
                flash('Invalid password. Please try again.', 'danger')
        else:
            flash('Username not found. Please register.', 'warning')
            return redirect('/register')

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()

        if check_username_exists(username, cursor):
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            register_user(username, password, cursor)
            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect('/login')
    
    return render_template('register.html')

@main.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@main.route('/history', methods=['GET'])
def history():
    conn = get_db_connection()
    cursor = conn.cursor()
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    cursor.execute("SELECT COUNT(*) FROM search_history")
    total_records = cursor.fetchone()[0]

    # Fetch food names and timestamps
    cursor.execute("SELECT food_name, timestamp FROM search_history ORDER BY timestamp DESC LIMIT ? OFFSET ?", (per_page, offset))
    history_records = cursor.fetchall()

    total_pages = (total_records + per_page - 1) // per_page

    return render_template('history.html', history_records=history_records, page=page, total_pages=total_pages)
