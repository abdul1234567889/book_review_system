from flask import Blueprint

bp = Blueprint('threading_demo', __name__)

from app.threading_demo import routes
