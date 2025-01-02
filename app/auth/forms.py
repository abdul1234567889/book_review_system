from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Regexp
from app.models import User
import re

def validate_password_strength(form, field):
    """
    Validate password has:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    - Minimum length of 8 characters
    """
    password = field.data
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character.')

def validate_username(form, field):
    """Validate username contains both letters and numbers"""
    username = field.data
    if not (re.search(r'[A-Za-z]', username) and re.search(r'\d', username)):
        raise ValidationError('Username must contain both letters and numbers.')

def validate_name(form, field):
    """Validate name contains only letters"""
    name = field.data
    if not re.match(r'^[A-Za-z]+$', name):
        raise ValidationError('Name must contain only letters.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=25),
        validate_username
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address'),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
        validate_password_strength
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50),
        validate_name
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50),
        validate_name
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')
