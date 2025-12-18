import os
from flask import Flask, render_template, url_for, flash, redirect, request, abort
from forms import RegistrationForm, LoginForm, BookForm, UserEditForm
from models import db, User, Book
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from functools import wraps
from ai_service import get_library_data, ask_ai


# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysupersecretkey12345'

# --- Database Configuration ---
if os.getenv('DATABASE_URL'):
    database_url = os.getenv('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Use absolute path to database
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Initialize Database ---
db.init_app(app)
# --- Auto create tables ---
with app.app_context():
    db.create_all()

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password, is_admin = False)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password!', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect (url_for('home'))


# --- Admin Routes ---
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    books = Book.query.all()
    return render_template('admin.html', title='Admin', users=users, books=books)

@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(
        original_username=user.username,
        original_email=user.email
    )

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data

        if user.id != current_user.id:
            user.is_admin = form.is_admin.data

        db.session.commit()
        flash(f'User {user.username} has been updated!', 'success')
        return redirect(url_for('admin_dashboard'))

    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.is_admin.data = user.is_admin

    return render_template(
        'user_edit.html',
        title='Edit User',
        form=form,
        user=user
    )


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete yourself!', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(user)
    db.session.commit()

    flash(f'User {user.username} has been deleted!', 'success')
    return redirect(url_for('admin_dashboard'))


# --- Error Handlers ---
@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


# --- Book Routes ---
@app.route('/books')
@login_required
def books_page():
    books = (
        Book.query
        .filter_by(user_id=current_user.id)
        .order_by(Book.date_added.desc())
        .all()
    )
    return render_template('books.html', books=books)

@app.route('/book/new', methods = ['GET', 'POST'])
@login_required
def new_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            genre=form.genre.data,
            status=form.status.data,
            price=form.price.data,
            owner=current_user)

        db.session.add(book)
        db.session.commit()

        flash(f' "{book.title}" has been added to you library!', 'success')
        return redirect(url_for('books_page'))
    return render_template('book_form.html', title = 'Add book', form=form, legend = 'Add New Book')


@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if book.owner != current_user and not current_user.is_admin:
        abort(403)
    form = BookForm()
    if form.validate_on_submit():
        # --- Update book ---
        book.title = form.title.data
        book.author = form.author.data
        book.genre = form.genre.data
        book.status = form.status.data
        book.price = form.price.data

        db.session.commit()
        flash(f'"{book.title}" has been updated!', 'success')

        if current_user.is_admin and book.owner != current_user:
            return redirect(url_for('admin_dashboard'))

        return redirect(url_for('books_page'))

    elif request.method == 'GET':
        form.title.data = book.title
        form.author.data = book.author
        form.genre.data = book.genre
        form.status.data = book.status
        form.price.data = book.price
    
    return render_template('book_form.html', 
                          title= book.title,
                          form=form, 
                          legend='Edit Book',
                          book=book)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    """Delete a book from user's library"""
    book = Book.query.get_or_404(book_id)
    
    if book.owner != current_user and not current_user.is_admin:
        abort(403)
    
    book_title = book.title 
    db.session.delete(book)
    db.session.commit()
    flash(f'"{book_title}" has been deleted from your library!', 'success')
    return redirect(url_for('books_page'))


# --- AI Route ---
@app.route('/ai-query', methods=['GET', 'POST'])
@login_required
def ai_query():
    response = None

    if request.method == 'POST':
        question = request.form.get('question', "").strip()
        library_data = get_library_data(question, current_user)

        response = ask_ai(
            question=question,
            library_data=library_data,
            is_admin=current_user.is_admin
        )

    return render_template("ai_query.html", response=response)

# -- Run the app ---
if __name__ == "__main__":
    app. run(debug=True)

