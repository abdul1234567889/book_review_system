import pytest
from app import db
from app.models import User
from flask_login import current_user
from flask import session
from bs4 import BeautifulSoup

def get_csrf_token(response):
    """Extract CSRF token from response HTML using BeautifulSoup"""
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})
    return csrf_token['value'] if csrf_token else None

def test_login_success(app, client, test_user):
    """Test successful login"""
    with app.test_client() as test_client:
        with app.app_context():
            db.session.add(test_user)
            db.session.commit()

            # First get the login page to get the CSRF token if enabled
            response = test_client.get('/auth/login')
            assert response.status_code == 200
            csrf_token = get_csrf_token(response)

            # Prepare login data
            login_data = {
                'username': 'testuser',
                'password': 'password123',
                'submit': 'Sign In'  # Add submit field
            }
            if csrf_token:
                login_data['csrf_token'] = csrf_token

            # Now post the login form
            response = test_client.post('/auth/login', 
                                      data=login_data, 
                                      follow_redirects=True)
            assert response.status_code == 200
            assert b'Login successful!' in response.data
            
            # Check session after successful login
            with test_client.session_transaction() as sess:
                assert '_user_id' in sess

def test_login_failure(app, client, test_user):
    """Test failed login"""
    with app.test_client() as test_client:
        with app.app_context():
            db.session.add(test_user)
            db.session.commit()

            # First get the login page to get the CSRF token if enabled
            response = test_client.get('/auth/login')
            csrf_token = get_csrf_token(response)

            # Prepare login data
            login_data = {
                'username': 'testuser',
                'password': 'wrongpassword',
                'submit': 'Sign In'  # Add submit field
            }
            if csrf_token:
                login_data['csrf_token'] = csrf_token

            response = test_client.post('/auth/login', 
                                      data=login_data, 
                                      follow_redirects=True)
            assert response.status_code == 200
            assert b'Invalid username or password' in response.data
            with test_client.session_transaction() as sess:
                assert '_user_id' not in sess

def test_register_success(app, client):
    """Test successful registration"""
    with app.test_client() as test_client:
        # First get the register page to get the CSRF token if enabled
        response = test_client.get('/auth/register')
        csrf_token = get_csrf_token(response)

        # Prepare registration data
        register_data = {
            'username': 'newuser123',
            'email': 'new@example.com',
            'password': 'Password123!',
            'first_name': 'New',
            'last_name': 'User',
            'submit': 'Register'  # Add submit field
        }
        if csrf_token:
            register_data['csrf_token'] = csrf_token

        response = test_client.post('/auth/register', 
                                  data=register_data, 
                                  follow_redirects=True)
        assert response.status_code == 200
        assert b'Congratulations, you are now a registered user!' in response.data
        
        with app.app_context():
            user = User.query.filter_by(username='newuser123').first()
            assert user is not None
            assert user.email == 'new@example.com'
            assert user.check_password('Password123!')

def test_register_duplicate_username(app, client, test_user):
    """Test registration with existing username"""
    with app.test_client() as test_client:
        with app.app_context():
            db.session.add(test_user)
            db.session.commit()

            # First get the register page to get the CSRF token if enabled
            response = test_client.get('/auth/register')
            csrf_token = get_csrf_token(response)

            # Prepare registration data
            register_data = {
                'username': 'testuser',
                'email': 'another@example.com',
                'password': 'Password123!',
                'first_name': 'Test',
                'last_name': 'User',
                'submit': 'Register'  # Add submit field
            }
            if csrf_token:
                register_data['csrf_token'] = csrf_token

            response = test_client.post('/auth/register', 
                                      data=register_data, 
                                      follow_redirects=True)
            assert response.status_code == 200
            assert b'Username already taken' in response.data

def test_logout(auth_client):
    """Test logout functionality"""
    with auth_client.session_transaction() as sess:
        assert '_user_id' in sess
    
    response = auth_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
    
    with auth_client.session_transaction() as sess:
        assert '_user_id' not in sess
