#Here is the frontend. Ensure the API base URL doesn't clash with other technologies you may use
#frontend.py
from nicegui import ui
import os
import requests

# Backend API base URL
BACKEND_URL = 'http://127.0.0.1:5001'

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ui.add_head_html('''
<style>
    body { background-color: #0F172A; color: #E2E8F0; font-family: 'Arial', sans-serif; }
    .card { background-color: #1E293B; color: #E2E8F0; border-radius: 10px; padding: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); }
    .button { background: linear-gradient(135deg, #10B981, #059669); color: white; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s; }
    .button:hover { transform: scale(1.05); }
    .input { background-color: #334155; color: white; border-radius: 8px; padding: 12px; border: 1px solid #475569; width: 100%; }
    .sidebar { background-color: #1E293B; height: 100vh; width: 250px; position: fixed; top: 0; left: 0; padding: 20px; }
    .sidebar a { color: #E2E8F0; display: block; padding: 10px; text-decoration: none; font-weight: bold; transition: 0.3s; }
    .sidebar a:hover { background-color: #334155; border-radius: 5px; }
</style>
''')

# Sidebar Component
def sidebar():
    with ui.column().classes('w-64 h-screen bg-gray-900 text-white fixed top-0 left-0 p-4'):
        ui.label("Navigation").classes('text-xl font-bold mb-4')
        ui.link("Dashboard", target='/dashboard').classes('block py-2 hover:text-green-400')
        ui.link("About Me", target='/about_me').classes('block py-2 hover:text-green-400')
        ui.link("Logout", target='/').classes('block py-2 text-red-400 hover:text-red-600')

# Dashboard Page
@ui.page('/dashboard')
def dashboard():
    sidebar()
    with ui.card().classes('w-3/4 mx-auto mt-10 card shadow-lg ml-72'):
        ui.label("Dashboard").classes('text-3xl font-bold mb-4')
        
        with ui.column().classes('w-full mt-6'):
            ui.label("Chatbot Assistant").classes('text-xl font-bold mb-2')
            chat_container = ui.column().classes('w-full h-96 overflow-y-auto bg-gray-800 p-4 rounded-lg')
            
            with ui.row().classes('w-full mt-4'):
                message_input = ui.input(placeholder='Type your message...').classes('input flex-grow')
                
                async def send_message():
                    if message_input.value.strip():
                        with chat_container:
                            ui.label(f"You: {message_input.value}").classes('text-green-400 mb-2')
                        
                        # Get username from localStorage
                        username = await ui.run_javascript("return localStorage.getItem('username')")
                        if not username:
                            ui.notify("Please log in first.", type="warning")
                            return
                        
                        # Send message and username to backend
                        response = requests.post(f'{BACKEND_URL}/api/chat', json={
                            'message': message_input.value,
                            'username': username
                        })
                        if response.status_code == 200:
                            bot_response = response.json().get('response', 'Error: No response')
                            with chat_container:
                                ui.label(f"Bot: {bot_response}").classes('text-blue-400 mb-2')
                        else:
                            ui.notify(f"Chat error: {response.status_code}", type="warning")
                        
                        message_input.value = ''
                        ui.run_javascript('chat_container.scrollTop = chat_container.scrollHeight')

                ui.button("Send", on_click=send_message).classes('button ml-2')

# About Company Page
@ui.page('/about_me')
def about_company():
    sidebar()
    with ui.card().classes('w-200 mx-auto mt-10 card shadow-lg ml-72'):
        ui.label("About Me").classes('text-3xl font-bold mb-4')
        ui.label("Hello, my name is Syed Abdullah.")
        ui.label("I am an aspiring Data scientist working as an intern at D-Cube Data Sciences.")
        ui.label("This project was created by using all sorts of technologies that I learned at my workplace.")

# Login Page
@ui.page('/')
def login():
    with ui.card().classes('w-96 mx-auto mt-20 card shadow-lg'):
        ui.image("https://static.vecteezy.com/system/resources/previews/010/849/613/large_2x/cyber-security-shield-free-vector.jpg").classes('mb-4')
        ui.label("Login").classes('text-2xl font-bold mb-4 text-center')
        username_input = ui.input(label='Username').classes('w-full input')
        password_input = ui.input(label='Password', password=True).classes('w-full input')
        ui.checkbox("Remember Me")
        
        def attempt_login():
            response = requests.post(f'{BACKEND_URL}/api/login', json={
                'username': username_input.value,
                'password': password_input.value
            })
            data = response.json()
            if data.get('success'):
                ui.notify(data['message'], type="positive")
                # Store username in localStorage
                ui.run_javascript(f"localStorage.setItem('username', '{username_input.value}'); window.location.href='/dashboard'")
            else:
                ui.notify(data['message'], type="warning")

        ui.button("Login", on_click=attempt_login).classes('button w-full mt-4')
        ui.link("Register", target='/registration').classes('text-green-400 mt-2 block text-center')
        ui.link("Forgot Password?", target='/reset_password').classes('text-sm text-blue-400 mt-2 block text-center')

# Registration Page
@ui.page('/registration')
def registration():
    with ui.card().classes('w-96 mx-auto mt-10 card shadow-lg'):
        ui.label("Welcome to Cyber Shield Advisor").classes('text-3xl font-bold mb-4')
        username_input = ui.input(label="Username").classes('input')
        password_input = ui.input(label="Password", password=True).classes('input')
        re_password_input = ui.input(label="Re-enter Password", password=True).classes('input')
        age_input = ui.number(label="Age").classes('input')
        location_input = ui.select(["USA", "UK", "Canada", "India", "Australia"], label="Location").classes('input')
        occupation_input = ui.select(["Student", "Software Engineer", "Data Scientist", "Teacher", "Other"], label="Occupation").classes('input')
        education_input = ui.select(["High School", "Bachelor's", "Master's", "PhD", "Other"], label="Education Level").classes('input')
        time_online_input = ui.number(label="Time Spent Online (hours/day)").classes('input')
        social_media_input = ui.number(label="Social Media Usage (hours/day)").classes('input')
        device_input = ui.select(["PC", "Laptop", "Smartphone", "Tablet", "Other"], label="Device Used").classes('input')
        antivirus_checkbox = ui.checkbox("Has Antivirus Installed")
        
        def register_user():
            if password_input.value != re_password_input.value:
                ui.notify("Passwords do not match.", type="warning")
                return
            
            response = requests.post(f'{BACKEND_URL}/api/register', json={
                'username': username_input.value,
                'password': password_input.value,
                'age': age_input.value,
                'location': location_input.value,
                'occupation': occupation_input.value,
                'education': education_input.value,
                'time_spent_online': time_online_input.value,
                'social_media_usage': social_media_input.value,
                'device_used': device_input.value,
                'has_antivirus': antivirus_checkbox.value
            })
            data = response.json()
            if data.get('success'):
                ui.notify(data['message'], type="positive")
                ui.run_javascript("window.location.href='/'")
            else:
                ui.notify(data['message'], type="warning")

        ui.button("Submit", on_click=register_user).classes('button w-full mt-4')
        ui.link("Back to Login", target='/').classes('text-blue-400 mt-2 block text-center')

# Forgot Password Page (Placeholder)
@ui.page('/reset_password')
def reset_password():
    with ui.card().classes('w-96 mx-auto mt-10 card shadow-lg'):
        ui.label("Reset Password").classes('text-3xl font-bold mb-4')
        ui.input(label="Enter your registered Email").classes('w-full input')
        ui.button("Reset").classes('button w-full mt-4')
        ui.link("Back to Login", target='/').classes('text-green-400 mt-2 block text-center')

# Run the Application
ui.run(title='Final Project', port=5000)
