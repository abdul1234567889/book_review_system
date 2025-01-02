from flask import render_template, jsonify, flash, redirect, url_for
from app.threading_demo import bp
from threading import Thread
import concurrent.futures
import time
import random
from app.models import Book
from sqlalchemy import func
from app import db
from app.threading_demo.sample_books import SAMPLE_BOOKS
from flask_login import login_required, current_user
from datetime import datetime, timezone

def process_books_chunk(chunk):
    """Process a chunk of books to calculate statistics"""
    stats = {
        'total_words': 0,
        'avg_title_length': 0,
        'genres': set()
    }
    
    for book in chunk:
        # Simulate intensive processing
        time.sleep(0.1)
        
        # Calculate word count from description
        if book.description:
            stats['total_words'] += len(book.description.split())
        
        # Calculate title length
        stats['avg_title_length'] += len(book.title)
        
        # Add genre
        if book.genre:
            stats['genres'].add(book.genre)
    
    if len(chunk) > 0:
        stats['avg_title_length'] /= len(chunk)
    
    return stats

def merge_stats(stats_list):
    """Merge statistics from multiple threads"""
    merged = {
        'total_words': 0,
        'avg_title_length': 0,
        'genres': set()
    }
    
    for stats in stats_list:
        merged['total_words'] += stats['total_words']
        merged['avg_title_length'] += stats['avg_title_length']
        merged['genres'].update(stats['genres'])
    
    if stats_list:
        merged['avg_title_length'] /= len(stats_list)
    
    merged['genres'] = list(merged['genres'])
    return merged

@bp.route('/')
@login_required
def index():
    return render_template('threading_demo/index.html')

@bp.route('/process/sequential')
@login_required
def process_sequential():
    start_time = time.time()
    
    # Get all books
    books = Book.query.all()
    
    # Process all books in a single thread
    stats = process_books_chunk(books)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    stats['processing_time'] = processing_time
    stats['method'] = 'sequential'
    stats['genres'] = list(stats['genres'])
    
    return jsonify(stats)

@bp.route('/process/threaded')
@login_required
def process_threaded():
    start_time = time.time()
    
    # Get all books
    books = Book.query.all()
    
    # Split books into chunks for parallel processing
    num_threads = 4
    chunk_size = len(books) // num_threads
    chunks = [books[i:i + chunk_size] for i in range(0, len(books), chunk_size)]
    
    # Process chunks in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit all tasks and get futures
        futures = [executor.submit(process_books_chunk, chunk) for chunk in chunks]
        
        # Wait for all futures to complete and get results
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # Merge results from all threads
    stats = merge_stats(results)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    stats['processing_time'] = processing_time
    stats['method'] = 'threaded'
    
    return jsonify(stats)

@bp.route('/process/both')
@login_required
def process_both():
    """Process books both sequentially and with threading for comparison"""
    # Sequential processing
    start_time = time.time()
    books = Book.query.all()
    sequential_stats = process_books_chunk(books)
    sequential_time = time.time() - start_time
    sequential_stats['processing_time'] = sequential_time
    sequential_stats['method'] = 'sequential'
    sequential_stats['genres'] = list(sequential_stats['genres'])
    
    # Threaded processing
    start_time = time.time()
    num_threads = 4
    chunk_size = len(books) // num_threads
    chunks = [books[i:i + chunk_size] for i in range(0, len(books), chunk_size)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_books_chunk, chunk) for chunk in chunks]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    threaded_stats = merge_stats(results)
    threaded_time = time.time() - start_time
    threaded_stats['processing_time'] = threaded_time
    threaded_stats['method'] = 'threaded'
    
    return jsonify({
        'sequential': sequential_stats,
        'threaded': threaded_stats,
        'speedup': sequential_time / threaded_time if threaded_time > 0 else 0
    })

@bp.route('/add_sample_books')
@login_required
def add_sample_books():
    """Add sample books to the database"""
    # Check if books already exist
    existing_isbns = set(book.isbn for book in Book.query.all())
    books_added = 0
    
    for book_data in SAMPLE_BOOKS:
        if book_data['isbn'] not in existing_isbns:
            book = Book(
                title=book_data['title'],
                author=book_data['author'],
                isbn=book_data['isbn'],
                genre=book_data['genre'],
                description=book_data['description'],
                added_by=current_user.id,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(book)
            books_added += 1
    
    if books_added > 0:
        db.session.commit()
        flash(f'Added {books_added} new sample books to the database!', 'success')
    else:
        flash('No new books were added. Sample books already exist in the database.', 'info')
    
    return redirect(url_for('threading_demo.index'))
