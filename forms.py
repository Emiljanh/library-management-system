from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DecimalField
from wtforms.validators import  DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from models import User

# --- Registration Form ---
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min = 2, max =20)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators= [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators= [DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
# --- Check if user already exists in the database ---
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken.')


# --- Login Form ---
class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators= [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


# --- Book Form ---
class BookForm(FlaskForm):
    title = StringField ('Title', validators = [DataRequired()])
    author = StringField ('Author', validators = [DataRequired()])
    genre = SelectField ('Genre', choices=[
                           ('Fiction', 'Fiction'),
                           ('Non-Fiction', 'Non-Fiction'),
                           ('Science', 'Science'),
                           ('History', 'History'),
                           ('Biography', 'Biography'),
                           ('Fantasy', 'Fantasy'),
                           ('Mystery', 'Mystery'),
                           ('Romance', 'Romance'),
                           ('Thriller', 'Thriller'),
                           ('Self-Help', 'Self-Help'),
                           ('Other', 'Other')
                       ],
                       validators = [DataRequired()])
    status = SelectField('Status', 
                        choices = [
                        ('To Read', 'To Read'),
                        ('Reading', 'Reading'),
                        ('Completed', 'Completed')   
                        ],
                        validators = [DataRequired()],
                        default = 'To Read')
    price = DecimalField('Price', 
                        validators = [DataRequired(), NumberRange(min=0)],
                        places =2)
    submit = SubmitField('Save Book')


# --- User Edit Form (for Admin) ---
class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Admin Status')
    submit = SubmitField('Update User')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already taken.')