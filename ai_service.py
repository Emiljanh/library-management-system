import os
from dotenv import load_dotenv
import openai
from models import db, User, Book
from sqlalchemy import func

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def is_personal_admin_question(question: str) -> bool:
    q = question.lower()
    keywords = ["my ", "me ", "mine", "myself"]
    return any(word in q for word in keywords)


def get_books_for_user(current_user):
    if current_user.is_admin:
        return Book.query.all()
    return Book.query.filter_by(user_id=current_user.id).all()


def get_library_data(question, current_user):
    q_lower = question.lower().strip()

    if current_user.is_admin and is_personal_admin_question(q_lower):
        books = Book.query.filter_by(user_id=current_user.id).all()
        admin_personal_mode = True
    else:
        books = get_books_for_user(current_user)
        admin_personal_mode = False

    if not books:
        return "No books found in the library."

    data = "Library Data:\n\n"
    
    data += "Books:\n"
    for book in books:
        owner = f" (Owner: {book.owner.username})" if current_user.is_admin and not admin_personal_mode else ""
        data += (
            f"- {book.title} by {book.author}, "
            f"Genre: {book.genre}, Status: {book.status}, "
            f"Price: ${book.price:.2f}{owner}\n"
        )

    # Statistics
    data += f"\nTotal Books: {len(books)}\n"
    total_value = sum(book.price for book in books)
    data += f"Total Value: ${total_value:.2f}\n"
    avg_price = total_value / len(books) if books else 0
    data += f"Average Price: ${avg_price:.2f}\n"
    
    # Genre
    genres = {}
    for book in books:
        genres[book.genre] = genres.get(book.genre, 0) + 1
    
    data += "\nBooks by Genre:\n"
    for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
        data += f"- {genre}: {count} books\n"
    
    # Status 
    statuses = {}
    for book in books:
        statuses[book.status] = statuses.get(book.status, 0) + 1
    
    data += "\nBooks by Status:\n"
    for status, count in statuses.items():
        data += f"- {status}: {count} books\n"
    
    # Admin-only
    if current_user.is_admin and not admin_personal_mode:
        users = User.query.all()
        user_books = {}
        for book in books:
            username = book.owner.username
            user_books[username] = user_books.get(username, 0) + 1
        
        data += "\nBooks per User:\n"
        for username, count in sorted(user_books.items(), key=lambda x: x[1], reverse=True):
            data += f"- {username}: {count} books\n"

    return data


def ask_ai(question, library_data, is_admin):
    """Send question and data to OpenAI"""
    try:
        system_message = (
            "You are a helpful library assistant. Answer questions based on the provided library data. "
            "Be friendly and concise. If asked about something not in the data, say so politely."
        )
        
        if is_admin:
            system_message += " You're assisting an admin who can see all users' data."
        else:
            system_message += " You're assisting a regular user viewing their personal library."
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Question: {question}\n\n{library_data}\n\nAnswer the question based on this data."}
            ]
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Sorry, there was an error connecting to AI: {str(e)}"