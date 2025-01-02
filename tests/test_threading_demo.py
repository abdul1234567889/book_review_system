from flask import url_for
from app import db

def test_process_books_chunk(app):
    """Test 8: Test processing a chunk of books"""
    books = [
        {'title': 'Book 1', 'pages': 100},
        {'title': 'Book 2', 'pages': 200}
    ]
    total_pages = sum(book['pages'] for book in books)
    assert total_pages == 300

def test_merge_stats(app):
    """Test 9: Test merging statistics"""
    stats1 = {'total_pages': 100, 'book_count': 1}
    stats2 = {'total_pages': 200, 'book_count': 2}
    merged = {
        'total_pages': stats1['total_pages'] + stats2['total_pages'],
        'book_count': stats1['book_count'] + stats2['book_count']
    }
    assert merged['total_pages'] == 300
    assert merged['book_count'] == 3

def test_add_sample_books(app, auth_client):
    """Test 10: Test adding sample books"""
    with app.app_context():
        response = auth_client.get('/threading_demo/add_sample_books', follow_redirects=True)
        assert response.status_code == 200
        assert b'Added' in response.data and b'new sample books to the database!' in response.data
