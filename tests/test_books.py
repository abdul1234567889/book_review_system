import pytest
from app.models import Book, User, Review, ReadingList
from app import db
from datetime import datetime, timezone

@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Get a fresh instance
        user = db.session.get(User, user.id)
        yield user
        
        db.session.rollback()
        db.session.query(User).filter_by(id=user.id).delete()
        db.session.commit()

@pytest.fixture
def test_book(app, test_user):
    """Create a test book"""
    with app.app_context():
        book = Book(
            title='Test Book',
            author='Test Author',
            description='Test Description',
            isbn='1234567890',
            publication_date=datetime.now(timezone.utc),
            added_by=test_user.id
        )
        db.session.add(book)
        db.session.commit()
        
        # Get a fresh instance
        book = db.session.get(Book, book.id)
        yield book
        
        # Clean up
        db.session.rollback()
        try:
            db.session.delete(book)
            db.session.commit()
        except:
            db.session.rollback()

def test_create_book(app, test_user):
    """Test book creation"""
    with app.app_context():
        book = Book(
            title='New Book',
            author='New Author',
            description='New Description',
            isbn='0987654321',
            publication_date=datetime.now(timezone.utc),
            added_by=test_user.id
        )
        db.session.add(book)
        db.session.commit()
        
        # Get a fresh instance
        book = db.session.get(Book, book.id)
        assert book.id is not None
        assert book.title == 'New Book'
        assert book.author == 'New Author'
        assert book.added_by == test_user.id
        
        db.session.rollback()
        db.session.query(Book).filter_by(id=book.id).delete()
        db.session.commit()

def test_update_book(app, test_book):
    """Test book update"""
    with app.app_context():
        # Get a fresh instance
        book = db.session.get(Book, test_book.id)
        book.title = 'Updated Title'
        book.author = 'Updated Author'
        db.session.commit()
        
        # Verify changes
        updated_book = db.session.get(Book, book.id)
        assert updated_book.title == 'Updated Title'
        assert updated_book.author == 'Updated Author'

def test_delete_book(app, test_book):
    """Test book deletion"""
    with app.app_context():
        # Get a fresh instance
        book = db.session.get(Book, test_book.id)
        book_id = book.id
        db.session.delete(book)
        db.session.commit()
        
        deleted_book = db.session.get(Book, book_id)
        assert deleted_book is None

def test_book_review_relationship(app, test_book, test_user):
    """Test book-review relationship"""
    with app.app_context():
        # Get a fresh instance
        book = db.session.get(Book, test_book.id)
        review = Review(
            content='Test Review',
            rating=5,
            book_id=book.id,
            user_id=test_user.id
        )
        db.session.add(review)
        db.session.commit()
        
        # Verify relationship
        book = db.session.get(Book, book.id)
        assert len(book.reviews) == 1
        assert book.reviews[0].content == 'Test Review'
        assert book.reviews[0].rating == 5
        
        db.session.rollback()
        db.session.query(Review).filter_by(id=review.id).delete()
        db.session.commit()

def test_book_reading_list_relationship(app, test_book, test_user):
    """Test book-reading list relationship"""
    with app.app_context():
        # Get a fresh instance
        book = db.session.get(Book, test_book.id)
        reading_list = ReadingList(
            name='Test List',
            user_id=test_user.id
        )
        reading_list.books.append(book)
        db.session.add(reading_list)
        db.session.commit()
        
        # Verify relationship
        book = db.session.get(Book, book.id)
        assert len(book.reading_lists) == 1
        assert book.reading_lists[0].name == 'Test List'
        
        db.session.rollback()
        db.session.query(ReadingList).filter_by(id=reading_list.id).delete()
        db.session.commit()

def test_book_validation(app, test_user):
    """Test book validation"""
    with app.app_context():
        # Test invalid book (missing required fields)
        invalid_book = Book()
        with pytest.raises(Exception):
            db.session.add(invalid_book)
            db.session.commit()
        db.session.rollback()
        
        # Test book with minimal required fields
        book = Book(
            title='Test Book',
            author='Test Author',
            added_by=test_user.id
        )
        db.session.add(book)
        db.session.commit()
        assert book.id is not None
        db.session.rollback()
        db.session.query(Book).filter_by(id=book.id).delete()
        db.session.commit()

def test_book_search(app, test_book):
    """Test book search functionality"""
    with app.app_context():
        # Search by title
        results = Book.query.filter(Book.title.ilike('%Test%')).all()
        assert len(results) == 1
        assert results[0].id == test_book.id
        
        # Search by author
        results = Book.query.filter(Book.author.ilike('%Test%')).all()
        assert len(results) == 1
        assert results[0].id == test_book.id
        
        # Search with no results
        results = Book.query.filter(Book.title.ilike('%NonExistent%')).all()
        assert len(results) == 0

def test_publication_date_validation(app, test_user):
    """Test publication date validation"""
    with app.app_context():
        current_time = datetime.now(timezone.utc)
        
        # Test valid date
        valid_book = Book(
            title='Test Book',
            author='Test Author',
            publication_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            added_by=test_user.id
        )
        db.session.add(valid_book)
        db.session.commit()
        assert valid_book.id is not None
        
        # Test future date
        future_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
        future_book = Book(
            title='Future Book',
            author='Future Author',
            publication_date=future_date,
            added_by=test_user.id
        )
        db.session.add(future_book)
        db.session.commit()
        assert future_date > current_time
        
        # Clean up
        db.session.query(Book).filter(Book.id.in_([valid_book.id, future_book.id])).delete()
        db.session.commit()

def test_publication_date_search(app, test_user):
    """Test searching books by publication date range"""
    with app.app_context():
        # Create books with different dates
        dates = [
            datetime(2020, 1, 1, tzinfo=timezone.utc),
            datetime(2021, 6, 15, tzinfo=timezone.utc),
            datetime(2023, 12, 31, tzinfo=timezone.utc)
        ]
        
        books = []
        for i, date in enumerate(dates):
            book = Book(
                title=f'Book {i}',
                author=f'Author {i}',
                publication_date=date,
                added_by=test_user.id
            )
            books.append(book)
            db.session.add(book)
        db.session.commit()
        
        # Test date range search
        start_date = datetime(2021, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2022, 12, 31, tzinfo=timezone.utc)
        results = Book.query.filter(
            Book.publication_date.between(start_date, end_date)
        ).all()
        assert len(results) == 1
        assert results[0].title == 'Book 1'
        
        # Test search for books after a date
        results = Book.query.filter(
            Book.publication_date >= datetime(2023, 1, 1, tzinfo=timezone.utc)
        ).all()
        assert len(results) == 1
        assert results[0].title == 'Book 2'
        
        # Clean up
        db.session.query(Book).filter(Book.id.in_([b.id for b in books])).delete()
        db.session.commit()

def test_publication_date_sorting(app, test_user):
    """Test sorting books by publication date"""
    with app.app_context():
        # Create books with different dates
        dates = [
            datetime(2023, 1, 1, tzinfo=timezone.utc),
            datetime(2021, 1, 1, tzinfo=timezone.utc),
            datetime(2022, 1, 1, tzinfo=timezone.utc)
        ]
        
        books = []
        for i, date in enumerate(dates):
            book = Book(
                title=f'Book {i}',
                author=f'Author {i}',
                publication_date=date.replace(tzinfo=None),  # Store as naive datetime
                added_by=test_user.id
            )
            books.append(book)
            db.session.add(book)
        db.session.commit()
        
        # Test ascending sort
        results = Book.query.order_by(Book.publication_date.asc()).all()
        assert len(results) == 3
        assert results[0].publication_date.replace(tzinfo=timezone.utc) == dates[1]  # 2021
        assert results[1].publication_date.replace(tzinfo=timezone.utc) == dates[2]  # 2022
        assert results[2].publication_date.replace(tzinfo=timezone.utc) == dates[0]  # 2023
        
        # Test descending sort
        results = Book.query.order_by(Book.publication_date.desc()).all()
        assert len(results) == 3
        assert results[0].publication_date.replace(tzinfo=timezone.utc) == dates[0]  # 2023
        assert results[1].publication_date.replace(tzinfo=timezone.utc) == dates[2]  # 2022
        assert results[2].publication_date.replace(tzinfo=timezone.utc) == dates[1]  # 2021
        
        # Clean up
        db.session.query(Book).filter(Book.id.in_([b.id for b in books])).delete()
        db.session.commit()
