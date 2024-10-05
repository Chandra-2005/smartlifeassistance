import pandas as pd
import numpy as np
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from flask import Flask, render_template, request, redirect, session, flash
import hashlib

app = Flask(__name__)
app.secret_key = '24124441K'


def get_db_connection():
    conn = sqlite3.connect('nutrition.db')
    conn.row_factory = sqlite3.Row
    return conn


weight_gain_data = pd.read_csv(r'C:\Users\dayan\final_project\PythonProject\datasets\weight_gain.csv')
weight_loss_data = pd.read_csv(r'C:\Users\dayan\final_project\PythonProject\datasets\weight_loss.csv')
disease_data = pd.read_csv(r'C:\Users\dayan\final_project\PythonProject\datasets\Disease.csv')
allergy_data = pd.read_csv(r'C:\Users\dayan\final_project\PythonProject\datasets\Allergy.csv')


def combine_datasets(goal):
    if goal.lower() == 'gain':
        return weight_gain_data
    elif goal.lower() == 'loss':
        return weight_loss_data
    else:
        raise ValueError("Goal must be 'gain' or 'loss'.")


def train_model():
    weight_gain_data['goal'] = 'gain'
    weight_loss_data['goal'] = 'loss'

    combined_data = pd.concat([weight_gain_data, weight_loss_data])

    le = LabelEncoder()
    combined_data['goal'] = le.fit_transform(combined_data['goal'])

    X = combined_data.drop(['goal'], axis=1).select_dtypes(include=[np.number])
    y = combined_data['goal']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    return model, le


model, label_encoder = train_model()

conn = sqlite3.connect('nutrition.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        phone_number TEXT,
        country TEXT
    )
''')

cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS recommended_foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        food_name TEXT,
        date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, food_name)  -- This ensures no duplicates
    )   
''')

cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        food_name TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
conn.commit()


def get_foods_to_avoid(allergy_data: pd.DataFrame, disease_data: pd.DataFrame, allergies: list, diseases: list) -> set:
    foods_to_avoid = set()
    for allergy in allergies:
        if allergy in allergy_data['Allergy'].values:
            related_foods = allergy_data.loc[allergy_data['Allergy'] == allergy, 'Related Foods'].values[0]
            foods_to_avoid.update(food.strip() for food in related_foods.split(', '))
    for disease in diseases:
        if disease in disease_data['Disease'].values:
            related_foods = disease_data.loc[disease_data['Disease'] == disease, 'Foods to Avoid'].values[0]
            foods_to_avoid.update(food.strip() for food in related_foods.split(', '))
    return foods_to_avoid


def check_username_exists(username):
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone() is not None


def register_user(username, password, email, phone_number, country):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO users (username, password, email, phone_number, country) VALUES (?, ?, ?, ?, ?)", 
                   (username, hashed_password, email, phone_number, country))
    conn.commit()


def validate_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    return cursor.fetchone() is not None


def is_vegetarian(food_name):
    non_veg_keywords = ['beef', 'pork', 'chicken', 'turkey', 'fish', 'seafood', 'rabbit', 'buffalo', 'egg', 'meat', 'bacon', 'ham', 'lamb', 'goat', 'steak', 'emu', 'ostrich', 'oyster']
    return not any(keyword in food_name.lower() for keyword in non_veg_keywords)


def recommend_food(user_id, age, weight, height, food_type, goal, allergies, diseases, preference):
    if user_id is None:
        raise ValueError("User ID cannot be None")

    food_data = combine_datasets(goal)

    valid_food_groups = {
        'breakfast': ['Breakfast Cereals', 'Dairy and Egg Products', 'Fruits'],
        'lunch': ['Meats', 'Prepared Meals', 'Salads'],
        'dinner': ['Meats', 'Prepared Meals', 'Soups and Sauces'],
        'snack': ['Snacks', 'Sweets', 'Nuts and Seeds'],
        'beverage': ['Beverages'],
    }

    filtered_foods = food_data[food_data['Food Group'].isin(valid_food_groups.get(food_type.lower(), []))]

    foods_to_avoid = get_foods_to_avoid(allergy_data, disease_data, allergies, diseases)

    filtered_recommendations = [
        food for food in filtered_foods['name'].values if food not in foods_to_avoid
    ]

    if preference:
        if preference.lower() == 'veg':
            filtered_recommendations = [
                food for food in filtered_recommendations if is_vegetarian(food)
            ]
        elif preference.lower() == 'non-veg':
            filtered_recommendations = [
                food for food in filtered_recommendations if not is_vegetarian(food)
            ]

    cursor.execute("SELECT food_name FROM recommended_foods")
    already_recommended_foods = {row[0] for row in cursor.fetchall()}

    final_recommendations = []
    for food in filtered_recommendations:
        if food not in already_recommended_foods:
            final_recommendations.append(food)
            if len(final_recommendations) == 5:  # Limit to 5 recommendations
                break

    for food in final_recommendations:
        cursor.execute('''INSERT INTO recommended_foods (user_id, food_name) VALUES (?, ?)''', (user_id, food))
        cursor.execute('''INSERT INTO search_history (user_id, food_name) VALUES (?, ?)''', (user_id, food))

    conn.commit()

    return final_recommendations


@app.route('/')
def home():
    return redirect('/login')


@app.route('/history')
def history():
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = session.get('user_id')

    cursor.execute("SELECT * FROM search_history WHERE user_id=?", (user_id,))
    history_records = cursor.fetchall()

    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_records = len(history_records)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_records = history_records[start:end]

    conn.close()

    return render_template('history.html', history_records=paginated_records, page=page, total=total_records, per_page=per_page)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        con_password = request.form['con_password']
        email = request.form['email']
        phone_number = request.form['phone_number']
        country = request.form['country']

        if password == con_password:
            if check_username_exists(username):
                flash('Username already exists.', 'danger')
            else:
                register_user(username, password, email, phone_number, country)
                flash('Registration successful!', 'success')
                return redirect('/login')
        else:
            flash('Passwords do not match.', 'danger')

    return render_template('register.html')


# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password fields are filled
        if not username:
            flash('Username field cannot be empty.', 'warning')
            return render_template('login.html')
        if not password:
            flash('Password field cannot be empty.', 'warning')
            return render_template('login.html')

        # Validate the username and password against the nutrition.db database
        if validate_user(username, password):
            # Connect to the database to get user details
            conn = sqlite3.connect('nutrition.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            conn.close()

            # Set session variables for the user
            session['user_id'] = user[0]
            session['username'] = username
            return redirect('/recommendation')
        else:
            # Remove or comment out the flash message for invalid login attempts.
            # flash('Invalid username or password. Please try again.', 'danger')
            pass  # Do nothing if login fails

    # Render the login page if the request method is GET
    return render_template('login.html')

@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    if request.method == 'POST':
        age = int(request.form['age'])
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        food_type = request.form['food_type']
        goal = request.form['goal']
        allergies = request.form.getlist('allergies')
        diseases = request.form.getlist('diseases')
        preference = request.form.get('preference')

        user_id = session.get('user_id')  
        
        if user_id is None:
            flash('You must be logged in to get recommendations.', 'danger')
            return redirect('/login')

        recommended_foods = recommend_food(user_id, age, weight, height, food_type, goal, allergies, diseases, preference)

        return render_template('results.html', recommended_foods=recommended_foods)

    return render_template('recommendation.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
