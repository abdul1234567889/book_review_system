from flask import Blueprint

bp = Blueprint('reading_lists', __name__, url_prefix='/reading_lists')

from app.reading_lists import routes
