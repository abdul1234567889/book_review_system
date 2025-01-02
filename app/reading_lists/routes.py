from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.reading_lists import bp
from app.reading_lists.forms import ReadingListForm
from app.models import ReadingList, Book, ReadingListItem

@bp.route('/', methods=['GET'])
@login_required
def index():
    reading_lists = ReadingList.query.filter_by(user_id=current_user.id).all()
    return render_template('reading_lists/index.html', reading_lists=reading_lists)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ReadingListForm()
    if form.validate_on_submit():
        reading_list = ReadingList(
            name=form.name.data,
            user_id=current_user.id
        )
        db.session.add(reading_list)
        db.session.commit()
        flash('Reading list created successfully!', 'success')
        return redirect(url_for('reading_lists.view', id=reading_list.id))
    return render_template('reading_lists/create.html', form=form)

@bp.route('/<int:id>', methods=['GET'])
@login_required
def view(id):
    reading_list = ReadingList.query.get_or_404(id)
    if reading_list.user_id != current_user.id:
        flash('You do not have permission to view this reading list.', 'error')
        return redirect(url_for('reading_lists.index'))
    available_books = Book.query.all()
    form = ReadingListForm()  # Create form instance for CSRF token
    return render_template('reading_lists/view.html', reading_list=reading_list, available_books=available_books, form=form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    reading_list = ReadingList.query.get_or_404(id)
    if reading_list.user_id != current_user.id:
        flash('You do not have permission to edit this reading list.', 'error')
        return redirect(url_for('reading_lists.index'))
    
    form = ReadingListForm(obj=reading_list)
    if form.validate_on_submit():
        reading_list.name = form.name.data
        db.session.commit()
        flash('Reading list updated successfully!', 'success')
        return redirect(url_for('reading_lists.view', id=reading_list.id))
    
    return render_template('reading_lists/edit.html', form=form, reading_list=reading_list)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    reading_list = ReadingList.query.get_or_404(id)
    if reading_list.user_id != current_user.id:
        flash('You do not have permission to delete this reading list.', 'error')
        return redirect(url_for('reading_lists.index'))
    
    db.session.delete(reading_list)
    db.session.commit()
    flash('Reading list deleted successfully!', 'success')
    return redirect(url_for('reading_lists.index'))

@bp.route('/<int:id>/add_book/<int:book_id>', methods=['POST'])
@login_required
def add_book(id, book_id):
    reading_list = ReadingList.query.get_or_404(id)
    if reading_list.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    book = Book.query.get_or_404(book_id)
    if book not in reading_list.books:
        reading_list.books.append(book)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Added "{book.title}" to your reading list!'
        })
    return jsonify({
        'success': False,
        'message': 'This book is already in your reading list.'
    })

@bp.route('/<int:id>/remove_book/<int:book_id>', methods=['POST'])
@login_required
def remove_book(id, book_id):
    reading_list = ReadingList.query.get_or_404(id)
    if reading_list.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    book = Book.query.get_or_404(book_id)
    if book in reading_list.books:
        reading_list.books.remove(book)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Removed "{book.title}" from your reading list!'
        })
    return jsonify({
        'success': False,
        'message': 'This book is not in your reading list.'
    })
