from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."


def create_app():
    """
    Application Factory: Creates and configures the Flask application.
    
    Setup Steps:
    1. Load configuration from config.py
    2. Initialize database and login manager
    3. Register blueprints for different modules
    4. Create database tables if not exist
    
    Returns:
        Flask application instance
    """
    from config import Config
    
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from .auth import auth_bp
    from .products import products_bp
    from .expenses import expenses_bp
    from .dashboard import dashboard_bp
    from .reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(expenses_bp, url_prefix="/expenses")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(reports_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
