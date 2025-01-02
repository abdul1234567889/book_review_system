from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class ReadingListForm(FlaskForm):
    name = StringField('List Name', validators=[
        DataRequired(),
        Length(min=1, max=100, message='List name must be between 1 and 100 characters')
    ])
    submit = SubmitField('Save Reading List')
