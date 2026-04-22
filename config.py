"""
Configuration Module: Application settings and environment variables

This module handles all configuration for the Smart Inventory Management System.

Environment Variables:
- SECRET_KEY: Flask session secret (generate with: python -c 'import os; print(os.urandom(24).hex())')
- DATABASE_URL: Database connection string (defaults to local SQLite)

Usage:
    In production, set these environment variables:
    export SECRET_KEY="your-secret-key-here"
    export DATABASE_URL="your-database-url"
    
For development, defaults are used (local SQLite database).
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """
    Application configuration class.
    
    Settings:
    - SECRET_KEY: Used for session management and CSRF protection
    - SQLALCHEMY_DATABASE_URI: Database connection string
    - SQLALCHEMY_TRACK_MODIFICATIONS: SQLAlchemy optimization
    """
    
    # Secret key for session management
    # In production: use strong random key (see docstring above)
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-key-change-in-production"
    )
    
    # Database configuration
    # In production: use PostgreSQL or MySQL
    # Default: SQLite database in project root
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'sepm.db')}"
    )
    
    # Disable SQLAlchemy modification tracking (performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
