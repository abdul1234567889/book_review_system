import pytest
from app import db
from app.models import User, Book, ReadingList, Review
from datetime import datetime, timezone

def test_user_password_hashing(app, test_user):
    """Test 1: Test password hashing and verification"""
    with app.app_context():
        db.session.add(test_user)
        assert not test_user.check_password('wrong_password')
        assert test_user.check_password('password123')

def test_reading_list_book_operations(app, test_reading_list, test_book):
    """Test 2: Test adding and removing books from reading list"""
    with app.app_context():
        # Add book to reading list
        db.session.add(test_reading_list)
        db.session.add(test_book)
        test_reading_list.books.append(test_book)
        db.session.commit()
        
        # Verify book was added
        assert test_book in test_reading_list.books
        
        # Remove book from reading list
        test_reading_list.books.remove(test_book)
        db.session.commit()
        
        # Verify book was removed
        assert test_book not in test_reading_list.books

def test_book_review_relationship(app, test_book, test_user):
    """Test 3: Test book and review relationship"""
    with app.app_context():
        db.session.add(test_book)
        db.session.add(test_user)
        
        review = Review(
            rating=5,
            content='Great book!',
            book_id=test_book.id,
            user_id=test_user.id,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(review)
        db.session.commit()
        
        # Verify review was added
        assert len(test_book.reviews) == 1
        assert test_book.reviews[0].content == 'Great book!'
        assert test_book.reviews[0].rating == 5
