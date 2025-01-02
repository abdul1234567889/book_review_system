from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.books import bp as books_bp
    from app.reading_lists import bp as reading_lists_bp
    from app.errors import init_error_handlers
    from app.threading_demo import bp as threading_demo_bp
    from app.faq import bp as faq_bp
    from app.faq.routes import init_socketio

    # Register blueprints first
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(reading_lists_bp, url_prefix='/reading_lists')
    app.register_blueprint(threading_demo_bp, url_prefix='/threading_demo')
    app.register_blueprint(faq_bp)  # No URL prefix for FAQ
    
    init_error_handlers(app)

    # Initialize Socket.IO after blueprints are registered
    socketio = init_socketio(app)

    return app
