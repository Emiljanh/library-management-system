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

def is_recommendation_question(question: str) -> bool:
    q = question.lower()
    recommendation_keywords = [
        "recommend", "suggestion", "suggest", "what should i read",
        "what to read", "looking for", "similar to", "like"
    ]
    return any(keyword in q for keyword in recommendation_keywords)


def get_books_for_user(current_user, exclude_own_books=False):
    if exclude_own_books:
        return Book.query.filter(Book.user_id != current_user.id).all()
    
    if current_user.is_admin:
        return Book.query.all()
    return Book.query.filter_by(user_id=current_user.id).all()


def get_library_data(question, current_user):
    q_lower = question.lower().strip()
    
    is_recommendation = is_recommendation_question(q_lower)

    if current_user.is_admin and is_personal_admin_question(q_lower):
        books = Book.query.filter_by(user_id=current_user.id).all()
        admin_personal_mode = True
    elif is_recommendation:
        books = get_books_for_user(current_user, exclude_own_books=True)
        admin_personal_mode = False
    else:
        books = get_books_for_user(current_user)
        admin_personal_mode = False

    if not books:
        if is_recommendation:
            return "No books found in the library from other users for recommendations."
        return "No books found in the library."

    data = "Library Data:\n\n"
    
    if is_recommendation:
        data += "Books available for recommendation (excluding your own books):\n"
    else:
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
            "You are a helpful library assistant. You MUST answer questions ONLY based on the provided library data. "
            "NEVER use external knowledge or suggest books not in the library data. "
            "If asked for recommendations, ONLY recommend books from the provided library data. "
            "If the library data doesn't contain enough information to answer a question, "
            "politely explain that you can only help with books in this library."
        )
        
        if is_admin:
            system_message += (
            " For admin users: use all system data unless the question contains personal words "
            "(my, me, mine, myself). Then answer only using the admin's own books."
            )
        else:
            system_message += "You're assisting a regular user viewing their personal library."
        
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