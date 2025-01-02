from flask import url_for
from app import db
import json

def test_create_reading_list(app, auth_client, test_user):
    """Test 6: Test reading list creation"""
    with app.app_context():
        response = auth_client.post('/reading_lists/create', data={
            'name': 'My New Reading List'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Reading list created successfully!' in response.data

def test_add_book_to_reading_list(app, auth_client, test_reading_list, test_book):
    """Test 7: Test adding book to reading list"""
    with app.app_context():
        db.session.add(test_reading_list)
        db.session.add(test_book)
        db.session.commit()
        
        response = auth_client.post(
            f'/reading_lists/{test_reading_list.id}/add_book/{test_book.id}',
            follow_redirects=True
        )
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['message'] == 'Added "Test Book" to your reading list!'
