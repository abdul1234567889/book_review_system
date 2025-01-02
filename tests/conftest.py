import pytest
from app import create_app, db
from app.models import User, Book, ReadingList, Review
from config import Config
from datetime import datetime, timezone
from flask_login import login_user
from flask_socketio import SocketIO

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    LOGIN_DISABLED = False
    SERVER_NAME = 'localhost'  # Required for url_for to work in tests

@pytest.fixture(scope='function')
def app():
    app = create_app(TestConfig)
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def socketio():
    return SocketIO(logger=False, engineio_logger=False)

@pytest.fixture(scope='function')
def socketio_app(app, socketio):
    socketio.init_app(app)
    return app

@pytest.fixture(scope='function')
def socketio_client(socketio_app, socketio):
    client = socketio_app.test_client()
    return socketio.test_client(socketio_app, flask_test_client=client)

@pytest.fixture(scope='function')
def test_user(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            created_at=datetime.now(timezone.utc)
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

@pytest.fixture(scope='function')
def test_book(app, test_user):
    with app.app_context():
        book = Book(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            genre='Test Genre',
            description='Test Description',
            added_by=test_user.id,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(book)
        db.session.commit()
        db.session.refresh(book)
        return book

@pytest.fixture(scope='function')
def test_reading_list(app, test_user):
    with app.app_context():
        reading_list = ReadingList(
            name='Test Reading List',
            user_id=test_user.id,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(reading_list)
        db.session.commit()
        db.session.refresh(reading_list)
        return reading_list

@pytest.fixture(scope='function')
def auth_client(app, client, test_user):
    with app.app_context():
        with client.session_transaction() as session:
            # Log in the user
            login_user(test_user)
            session['_user_id'] = str(test_user.id)
            session['_fresh'] = True
        return client
