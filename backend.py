#Here is the flask based backend. NOTE: If you plan on using this code ensure you change the MySQL Configuration details like the username and password
#backend.py
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
from flask_cors import CORS
import os
import pandas as pd

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')

# MySQL configurations
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'host_nm')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'user_nm')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'user_pw')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'cyber_radar')

mysql = MySQL(app)

# Load Excel data
EXCEL_FILE = 'cyber_data.xlsx'  # Ensure this file exists in the same directory as backend.py
try:
    df = pd.read_excel(EXCEL_FILE)
except FileNotFoundError:
    print(f"Error: {EXCEL_FILE} not found. Please provide the Excel file.")
    df = pd.DataFrame()

# Registration Endpoint with Advice
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    age = data.get('age')
    location = data.get('location')
    occupation = data.get('occupation')
    education = data.get('education')
    time_spent_online = data.get('time_spent_online')
    social_media_usage = data.get('social_media_usage')
    device_used = data.get('device_used')
    has_antivirus = data.get('has_antivirus', False)

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({'success': False, 'message': 'Username already exists'}), 409

    cursor.execute(
        "INSERT INTO users (username, password, age, location, occupation, education, time_spent_online, social_media_usage, device_used, has_antivirus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (username, hashed_password, age, location, occupation, education, time_spent_online, social_media_usage, device_used, has_antivirus)
    )
    mysql.connection.commit()
    cursor.close()

    advice = generate_advice(age, location, occupation, education, time_spent_online, social_media_usage, device_used, has_antivirus)
    
    return jsonify({'success': True, 'message': 'Registration successful', 'advice': advice}), 201

# Login Endpoint
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'success': True, 'message': 'Login successful', 'username': username}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Login Error: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

# Chatbot Endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower().strip()
    username = data.get('username')  # Expect username from frontend

    if not username:
        return jsonify({'success': False, 'response': 'Username required. Please log in.'}), 400

    # Fetch user data from MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({'success': False, 'response': 'User not found. Please log in.'}), 404

    # Extract user data
    age = user['age']
    location = user['location']
    occupation = user['occupation']
    education = user['education']
    time_spent_online = user['time_spent_online']
    social_media_usage = user['social_media_usage']
    device_used = user['device_used']
    has_antivirus = user['has_antivirus']

    # Chatbot responses
    if "hello" in message or "hi" in message:
        response = "Hello! How can I assist you today?"
    elif "advice" in message or "cybersecurity" in message or "safety" in message:
        advice = generate_advice(age, location, occupation, education, time_spent_online, social_media_usage, device_used, has_antivirus)
        response = "Here’s some personalized cybersecurity advice for you:\n" + "\n".join(advice)
    elif "fuck" or "doodoo head" in message:
        response = "Please refrain from using provocative language"
    elif "Betrayed" in message:
        response = "Yeah, history does repeat itself"
    elif "Who are you" in message:
        response = "Hi, the creater of this mini project is named Syed Abdullah. He is quite the cutie patootie and has been working on this project for 2 months. His OU ID is 1289-22-861-042."
    elif "data science" in message:
        response = "Data science involves extracting insights from data using techniques like machine learning, statistics, and visualization. What specific aspect are you interested in?"
    elif "project" in message:
        response = "This project uses NiceGUI as a frontend and Flask as a backend with MySQL integration! This project has taken 2 months to create. The NiceGUI library was used to create a frontend with buttons, drop down menus, images, sidebars etc."
    elif "bye" in message or "goodbye" in message:
        response = "Goodbye! Feel free to return if you need more help."
    else:
        response = "I'm here to assist! Could you provide more context or ask a specific question?"

    return jsonify({'success': True, 'response': response}), 200

# Advice Generation Function
def generate_advice(age, location, occupation, education, time_spent_online, social_media_usage, device_used, has_antivirus):
    advice_list = []

    # Convert inputs to appropriate types
    age = float(age) if age else 0
    time_spent_online = float(time_spent_online) if time_spent_online else 0
    social_media_usage = float(social_media_usage) if social_media_usage else 0
    has_antivirus = bool(has_antivirus)

    # Derive Age_Group
    age_group = 'young' if age < 25 else 'adult' if age <= 40 else 'senior'

    # Compare with Excel data
    if not df.empty:
        # Filter similar profiles
        similar_profiles = df[
            (df['Occupation'] == occupation) &
            (df['Location'] == location) &
            (df['Age_Group'] == age_group)
        ]

        if not similar_profiles.empty:
            # Top 3 crime types
            common_crimes = similar_profiles['Crime_Type'].value_counts().index.tolist()[:3]
            if common_crimes:
                crime_list = ", ".join(common_crimes)
                advice_list.append(f"Based on similar profiles ({occupation} in {location}, {age_group}), the top 3 cybercrimes you might face are: {crime_list}. Stay vigilant!")

            # Average financial loss
            avg_loss = similar_profiles['Financial_Loss'].mean()
            if avg_loss > 0:
                advice_list.append(f"Similar users have lost an average of ${avg_loss:.2f} to cybercrimes. Protect your finances with strong passwords.")

        # Time spent online vs. average for occupation
        avg_time_by_occupation = df[df['Occupation'] == occupation]['Time_Spent_Online'].mean()
        if time_spent_online > avg_time_by_occupation * 1.5:
            advice_list.append(f"You spend more time online ({time_spent_online} hrs) than the average {occupation} ({avg_time_by_occupation:.1f} hrs). Limit exposure to risky sites.")

        # Social media usage vs. age group
        avg_social_by_age = df[df['Age_Group'] == age_group]['Social_Media_Usage'].mean()
        if social_media_usage > avg_social_by_age * 1.5:
            advice_list.append(f"Your social media usage ({social_media_usage} hrs) exceeds the {age_group} average ({avg_social_by_age:.1f} hrs). Watch out for phishing scams.")

        # Education level comparison
        avg_time_by_education = df[df['Education_Level'] == education]['Time_Spent_Online'].mean()
        if time_spent_online > avg_time_by_education * 1.5:
            advice_list.append(f"Your online time ({time_spent_online} hrs) exceeds the average for {education} holders ({avg_time_by_education:.1f} hrs). Be cautious.")

    # General rules
    if age_group == 'young' and occupation == 'Student':
        advice_list.append("As a young student, avoid sharing personal info in online forums.")
    if time_spent_online > 8:
        advice_list.append("Spending over 8 hours online daily increases your risk. Use a VPN on public networks.")
    if social_media_usage > 4:
        advice_list.append("High social media use (>4 hrs/day) makes you a target for social engineering. Verify friend requests.")
    if not has_antivirus:
        advice_list.append("No antivirus detected. Install one to guard against malware.")
    if device_used == "Smartphone":
        advice_list.append("Smartphone users: Keep your OS updated and avoid unverified apps.")
    if occupation in ["Student", "Teacher"] and age_group == "young":
        advice_list.append("Young students/teachers: Be wary of fake educational offers or chat scams.")
    if location == "USA" and social_media_usage > 3:
        advice_list.append("In the USA with high social media use, beware of identity theft risks.")

    return advice_list if advice_list else ["No specific advice at this time. Stay safe online!"]

if __name__ == '__main__':
    app.run(debug=True, port=5001)
