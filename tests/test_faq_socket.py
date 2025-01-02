import pytest
from flask import url_for
from app.faq.routes import FAQS, init_socketio
from flask_socketio import SocketIO
from app import create_app, db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    SERVER_NAME = 'localhost'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def socketio_app(app):
    """Initialize Socket.IO with the app"""
    socketio = init_socketio(app)
    return socketio

def test_faq_page_loads(app):
    """Test that the FAQ page loads successfully"""
    with app.test_client() as test_client:
        with app.app_context():
            response = test_client.get('/faq')
            assert response.status_code == 200
            assert b'Frequently Asked Questions' in response.data

def test_socket_connection(socketio_app, app):
    """Test socket.io connection"""
    flask_test_client = app.test_client()
    socketio_test_client = socketio_app.test_client(app, flask_test_client=flask_test_client)
    assert socketio_test_client.is_connected()
    
    # Wait for the connection event to be processed
    received = socketio_test_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'connected'
    
    # Send a test event and check response
    socketio_test_client.emit('ask_question', {'question': 'test'})
    received = socketio_test_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'answer'
    # Check for prompt for more specific information
    assert 'more specific' in received[0]['args'][0]['response'].lower()

def test_question_response(socketio_app, app):
    """Test asking a question through socket.io"""
    flask_test_client = app.test_client()
    socketio_test_client = socketio_app.test_client(app, flask_test_client=flask_test_client)
    assert socketio_test_client.is_connected()
    
    # Wait for the connection event to be processed
    received = socketio_test_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'connected'
    
    # Test with a question about account creation
    socketio_test_client.emit('ask_question', {'question': 'How do I create an account?'})
    received = socketio_test_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'answer'
    assert 'Click on Register' in received[0]['args'][0]['response']

    # Test with a question about book addition
    socketio_test_client.emit('ask_question', {'question': 'How do I add a book?'})
    received = socketio_test_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'answer'
    assert 'Add New Book' in received[0]['args'][0]['response']

    # Test with an unknown question
    socketio_test_client.emit('ask_question', {'question': 'What is the meaning of life?'})
    received = socketio_test_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'answer'
    # Check for any valid response about the system
    assert any(topic in received[0]['args'][0]['response'].lower() for topic in ['book', 'system', 'review'])
