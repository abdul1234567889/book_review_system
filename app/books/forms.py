from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DecimalField, DateField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app.models import Book

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    author = StringField('Author', validators=[DataRequired(), Length(max=200)])
    isbn = StringField('ISBN', validators=[Optional(), Length(max=13)])
    genre = SelectField('Genre', choices=[
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('mystery', 'Mystery'),
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('biography', 'Biography'),
        ('history', 'History'),
        ('other', 'Other')
    ])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    publication_date = DateField('Publication Date', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Add Book')

    def validate_isbn(self, field):
        if field.data:
            if Book.is_isbn_taken(field.data):
                raise ValidationError('A book with this ISBN already exists in the system.')

class ReviewForm(FlaskForm):
    rating = DecimalField('Rating (1-5)', validators=[DataRequired()], places=1)
    content = TextAreaField('Review', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Submit Review')
