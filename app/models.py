from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from app import db, login_manager
from sqlalchemy.orm import validates

# Observer Pattern Implementation
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    reviews = db.relationship('Review', backref='user', lazy=True)
    reading_lists = db.relationship('ReadingList', backref='user', lazy=True)
    books = db.relationship('Book', backref='added_by_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model, Subject):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, index=True)
    genre = db.Column(db.String(50))
    description = db.Column(db.Text)
    publication_date = db.Column(db.DateTime)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    reviews = db.relationship('Review', backref='book', lazy=True, cascade='all, delete-orphan')
    reading_lists = db.relationship('ReadingList', secondary='reading_list_items', back_populates='books')

    @staticmethod
    def is_isbn_taken(isbn):
        """Check if a book with the given ISBN already exists."""
        return Book.query.filter_by(isbn=isbn).first() is not None

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    @validates('rating')
    def validate_rating(self, key, rating):
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValueError("Rating must be an integer between 1 and 5")
        return rating

class ReadingList(db.Model):
    __tablename__ = 'reading_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    books = db.relationship('Book', secondary='reading_list_items', back_populates='reading_lists')

class ReadingListItem(db.Model):
    __tablename__ = 'reading_list_items'
    
    reading_list_id = db.Column(db.Integer, db.ForeignKey('reading_lists.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))
