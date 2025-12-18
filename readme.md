📚 Library Management System
A full-stack web application for managing personal book collections with AI-powered natural language queries. Built with Flask and OpenAI API to demonstrate modern web development skills.

Live Demo: https://library-management-4p5k.onrender.com

🎯 Project Overview
 The application allows users to track their reading lists, manage book collections, and interact with their library data using natural language queries powered by AI.

Demo Credentials:
Admin: admin@library.com / admin1234
Regular User: Register your own account


✨ Features
For All Users
Secure user authentication (register, login, logout)
Personal book library management (add, edit, delete books)
Statistics dashboard with visual cards
AI-powered natural language queries about your books
Responsive design that works on all devices

For Administrators
User management (view, edit, delete users)
System-wide book oversight
Comprehensive statistics across all users
Full administrative controls


🛠️ Tech Stack
Backend:
Python 3.10+
Flask (Web Framework)
SQLAlchemy (ORM)
SQLite (Database)
Flask-Login (Authentication)
Flask-Bcrypt (Password Hashing)

Frontend:
HTML5 & Jinja2 Templates
Bootstrap 5 (Responsive Design)

AI Integration:
OpenAI API (GPT-3.5-turbo)
Custom query processing

Deployment:
Render.com (Cloud Hosting)
Gunicorn (WSGI Server)

🚀 Installation & Setup
Prerequisites
Python3
pip (Python package manager)
OpenAI API key

Local Installation
1.Clone the repository
bashgit clone https://github.com/Emiljanh/library-management-system.git
cd library-management-system

2.Create virtual environment
bashpython3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

3.Install dependencies
bashpip install -r requirements.txt

4.Set up environment variables
Create a .env file in the project root:
envOPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here

Generate a secure SECRET_KEY:
bashpython3 -c "import secrets; print(secrets.token_hex(32))"

5.Initialize the database
The database will be created automatically when you run the app for the first time.

6.Run the application
bashpython app.py

7.Access the application
Open your browser and navigate to: http://127.0.0.1:5000


🧪 Testing
Manual testing was performed covering:
User authentication flows
Book CRUD operations
Admin functionality
AI Assistant queries
UI/UX responsiveness
Security and permissions

See manual_test.md for detailed test results.

📖 Usage
Regular Users:
Register a new account
Add books to your library with title, author, genre, status, and price
View your collection with statistics
Edit or delete books
Use AI Assistant to query your library naturally

Administrators:
Login with admin credentials
Access Admin Dashboard from navigation
Manage all users and books
View system-wide statistics
Query entire library database with AI

🎓 What I Learned
This project helped me develop and strengthen:
Full-Stack Development: Building complete web applications from database to UI
RESTful Design: Creating logical and maintainable route structures
Database Design: Implementing relationships and proper data modeling
Authentication & Authorization: Securing applications with role-based access
API Integration: Working with third-party APIs (OpenAI)
Deployment: Deploying applications to online platforms
