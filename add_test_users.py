#!/usr/bin/env python3
"""Add test staff users to the database"""

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Test staff users
    staff_users = [
        ('rajesh_kumar', 'staff123'),
        ('priya_sharma', 'staff123'),
        ('amit_patel', 'staff123'),
    ]
    
    for username, password in staff_users:
        existing = User.query.filter_by(username=username).first()
        if not existing:
            user = User(username=username, role='staff')
            user.set_password(password)
            db.session.add(user)
            print(f"Created user: {username}")
        else:
            print(f"User already exists: {username}")
    
    db.session.commit()
    
    # Display all users
    all_users = User.query.all()
    print(f"\nTotal users: {len(all_users)}")
    for user in all_users:
        print(f"  - {user.username} ({user.role})")
