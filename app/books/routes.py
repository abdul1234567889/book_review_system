from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.books import bp
from app.models import Book, Review, ReadingList, db
from app.books.forms import BookForm, ReviewForm
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

@bp.route('/books')
@login_required
def book_list():
    books = Book.query.all()
    return render_template('books/book_list.html', title='Books', books=books)

@bp.route('/books/search')
@login_required
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('books.book_list'))
    
    # Search in title, author, genre, and description
    books = Book.query.filter(
        or_(
            Book.title.ilike(f'%{query}%'),
            Book.author.ilike(f'%{query}%'),
            Book.genre.ilike(f'%{query}%'),
            Book.description.ilike(f'%{query}%')
        )
    ).all()
    
    return render_template('books/book_list.html', 
                         title='Search Results', 
                         books=books, 
                         search_query=query)

@bp.route('/book/add', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        try:
            book = Book(
                title=form.title.data,
                author=form.author.data,
                isbn=form.isbn.data,
                genre=form.genre.data,
                description=form.description.data,
                publication_date=form.publication_date.data,
                added_by=current_user.id
            )
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('books.book_list'))
        except IntegrityError:
            db.session.rollback()
            flash('A book with this ISBN already exists in the system.', 'error')
    return render_template('books/book_form.html', title='Add Book', form=form)

@bp.route('/book/<int:book_id>')
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    reviews = Review.query.filter_by(book_id=book_id).all()
    return render_template('books/book_detail.html', title=book.title, book=book, reviews=reviews)

@bp.route('/book/<int:book_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            rating=form.rating.data,
            content=form.content.data,
            book_id=book_id,
            user_id=current_user.id,
            created_at=datetime.utcnow()
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been added!', 'success')
        return redirect(url_for('books.book_detail', book_id=book_id))
    return render_template('books/review_form.html', title=f'Review {book.title}', form=form, book=book)

@bp.route('/reading-lists')
@login_required
def reading_lists():
    lists = ReadingList.query.filter_by(user_id=current_user.id).all()
    return render_template('books/reading_lists.html', title='Reading Lists', lists=lists)
