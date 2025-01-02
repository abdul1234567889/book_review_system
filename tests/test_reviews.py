import pytest
from app.models import Review, Book, User
from app import db
from datetime import datetime, timezone
import time

@pytest.fixture
def test_review(app, test_user, test_book):
    """Create a test review"""
    with app.app_context():
        review = Review(
            content='Test Review Content',
            rating=4,
            book_id=test_book.id,
            user_id=test_user.id
        )
        db.session.add(review)
        db.session.commit()
        
        # Get a fresh instance
        review = db.session.get(Review, review.id)
        yield review
        
        # Clean up
        db.session.rollback()
        try:
            db.session.delete(review)
            db.session.commit()
        except:
            db.session.rollback()

def test_create_review(app, test_user, test_book):
    """Test review creation"""
    with app.app_context():
        review = Review(
            content='New Review Content',
            rating=5,
            book_id=test_book.id,
            user_id=test_user.id
        )
        db.session.add(review)
        db.session.commit()
        
        # Get a fresh instance
        review = db.session.get(Review, review.id)
        assert review.id is not None
        assert review.content == 'New Review Content'
        assert review.rating == 5
        assert review.book_id == test_book.id
        assert review.user_id == test_user.id
        
        db.session.rollback()
        db.session.query(Review).filter_by(id=review.id).delete()
        db.session.commit()

def test_update_review(app, test_review):
    """Test review update"""
    with app.app_context():
        # Get a fresh instance
        review = db.session.get(Review, test_review.id)
        old_timestamp = review.created_at
        
        # Wait a bit to ensure timestamp changes
        time.sleep(0.1)
        
        review.content = 'Updated Review Content'
        review.rating = 3
        db.session.commit()
        
        # Verify changes
        updated_review = db.session.get(Review, review.id)
        assert updated_review.content == 'Updated Review Content'
        assert updated_review.rating == 3
        assert updated_review.created_at > old_timestamp

def test_delete_review(app, test_review):
    """Test review deletion"""
    with app.app_context():
        # Get a fresh instance
        review = db.session.get(Review, test_review.id)
        review_id = review.id
        db.session.delete(review)
        db.session.commit()
        
        deleted_review = db.session.get(Review, review_id)
        assert deleted_review is None

def test_review_user_relationship(app, test_review):
    """Test review-user relationship"""
    with app.app_context():
        assert test_review.user is not None
        assert test_review.user.id == test_review.user_id

def test_review_book_relationship(app, test_review):
    """Test review-book relationship"""
    with app.app_context():
        assert test_review.book is not None
        assert test_review.book.id == test_review.book_id

def test_review_validation(app, test_user, test_book):
    """Test review validation"""
    with app.app_context():
        # Test invalid review (missing required fields)
        invalid_review = Review()
        with pytest.raises(Exception):
            db.session.add(invalid_review)
            db.session.commit()
        db.session.rollback()

        # Test invalid rating (out of range)
        with pytest.raises(ValueError, match="Rating must be an integer between 1 and 5"):
            Review(
                content='Test Review',
                rating=6,  # Invalid rating > 5
                book_id=test_book.id,
                user_id=test_user.id
            )

        # Test valid review
        valid_review = Review(
            content='Test Review',
            rating=5,
            book_id=test_book.id,
            user_id=test_user.id
        )
        db.session.add(valid_review)
        db.session.commit()

def test_review_queries(app, test_review, test_user, test_book):
    """Test review queries"""
    with app.app_context():
        # Get fresh instances
        review = db.session.get(Review, test_review.id)
        user = db.session.get(User, test_user.id)
        book = db.session.get(Book, test_book.id)
        
        # Test getting reviews by user
        user_reviews = Review.query.filter_by(user_id=user.id).all()
        assert len(user_reviews) == 1
        assert user_reviews[0].id == review.id
        
        # Test getting reviews by book
        book_reviews = Review.query.filter_by(book_id=book.id).all()
        assert len(book_reviews) == 1
        assert book_reviews[0].id == review.id
        
        # Test getting reviews by rating
        rated_reviews = Review.query.filter_by(rating=review.rating).all()
        assert len(rated_reviews) > 0
        assert any(r.id == review.id for r in rated_reviews)

def test_review_timestamps(app, test_user, test_book):
    """Test review timestamps"""
    with app.app_context():
        review = Review(
            content='Timestamp Test Review',
            rating=4,
            book_id=test_book.id,
            user_id=test_user.id
        )
        db.session.add(review)
        db.session.commit()
        
        # Get a fresh instance
        review = db.session.get(Review, review.id)
        assert review.created_at is not None
        assert isinstance(review.created_at, datetime)
        
        # Test timestamp update
        old_timestamp = review.created_at
        time.sleep(0.1)  # Wait a bit to ensure timestamp changes
        review.content = 'Updated Text'
        db.session.commit()
        
        # Get a fresh instance and verify timestamp was updated
        review = db.session.get(Review, review.id)
        assert review.created_at > old_timestamp
        
        db.session.rollback()
        db.session.query(Review).filter_by(id=review.id).delete()
        db.session.commit()

def test_review_cascade_delete(app, test_user, test_book):
    """Test cascade delete behavior"""
    with app.app_context():
        # Get fresh instances
        book = db.session.get(Book, test_book.id)
        
        review = Review(
            content='Cascade Delete Test',
            rating=4,
            book_id=book.id,
            user_id=test_user.id
        )
        db.session.add(review)
        db.session.commit()
        
        review_id = review.id
        
        # Delete the book and verify the review is also deleted
        db.session.delete(book)
        db.session.commit()
        
        deleted_review = db.session.get(Review, review_id)
        assert deleted_review is None
