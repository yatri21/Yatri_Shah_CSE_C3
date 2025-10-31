#!/usr/bin/env python3
"""
Database initialization script for Study Buddy
Run this script to create the database and populate it with sample data
"""

from backend.app import create_app
from backend.models import db, ChatMessage

def init_database():
    """Initialize the database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate them (for development)
        db.drop_all()
        db.create_all()
        
        print("Database tables created successfully!")
        print("Sample data has been added.")
        print("\nDemo accounts:")
        print("Username: demo, Password: password")
        print("Username: student, Password: study123")
        print("\nNew Features:")
        print("- AI Study Assistant (Chat)")
        print("- Progress tracking with database")
        print("- Dark/Light theme toggle")
        print("\nDatabase file: study_buddy.db")

if __name__ == '__main__':
    init_database()