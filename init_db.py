#!/usr/bin/env python3
"""
Database Initialization Script

This script initializes the database and creates the first admin user.
Run this once on first deployment.

Usage:
    python3 init_db.py

The script will:
1. Create all database tables
2. Create a default admin user (username: admin, password: admin123)
3. Exit safely if tables/users already exist
"""

from app import create_app, db
from app.models import User


def init_database():
    """Initialize database and create default admin user"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Smart Inventory Management System - Database Initialization")
        print("=" * 60)
        
        # Create all tables
        print("\n1. Creating database tables...")
        try:
            db.create_all()
            print("   ✓ Database tables created successfully")
        except Exception as e:
            print(f"   ✗ Error creating tables: {e}")
            return False
        
        # Check if admin user exists
        print("\n2. Checking for default admin user...")
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print("   ✓ Admin user already exists")
            print("     Username: admin")
        else:
            print("   Creating default admin user...")
            try:
                admin = User(username='admin', role='admin')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("   ✓ Default admin user created successfully")
                print("     Username: admin")
                print("     Password: admin123")
                print("\n   ⚠️  IMPORTANT: Change this password in production!")
            except Exception as e:
                print(f"   ✗ Error creating admin user: {e}")
                db.session.rollback()
                return False
        
        # Create test staff users
        print("\n3. Creating test staff users...")
        staff_users = [
            ('rajesh_kumar', 'staff123'),
            ('priya_sharma', 'staff123'),
            ('amit_patel', 'staff123'),
        ]
        
        for username, password in staff_users:
            staff_user = User.query.filter_by(username=username).first()
            if not staff_user:
                try:
                    staff_user = User(username=username, role='staff')
                    staff_user.set_password(password)
                    db.session.add(staff_user)
                except Exception as e:
                    print(f"   ✗ Error creating staff user {username}: {e}")
                    db.session.rollback()
                    continue
        
        try:
            db.session.commit()
            print("   ✓ Test staff users created successfully")
            for username, password in staff_users:
                staff_user = User.query.filter_by(username=username).first()
                if staff_user:
                    print(f"     - {username} / {password}")
        except Exception as e:
            print(f"   ✗ Error saving staff users: {e}")
            db.session.rollback()
        
        # Display summary
        print("\n4. Database Summary:")
        user_count = User.query.count()
        print(f"   - Total users: {user_count}")
        print(f"   - Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        print("\n" + "=" * 60)
        print("Database initialization complete!")
        print("=" * 60)
        print("\nYou can now run the application:")
        print("  python3 run.py")
        print("\nDefault login credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n⚠️  Remember to change the password in production!")
        print("=" * 60)
        
        return True


if __name__ == '__main__':
    init_database()
