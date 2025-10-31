#!/usr/bin/env python3
"""
Simple database viewer for Study Buddy
Shows current data in the database
"""

from backend.app import create_app
from backend.models import db, User, StudyCard, StudySession, Progress

def view_database():
    """Display current database contents"""
    app = create_app()
    
    with app.app_context():
        print("=== STUDY BUDDY DATABASE CONTENTS ===\n")
        
        # Users
        users = User.query.all()
        print(f"USERS ({len(users)}):")
        for user in users:
            print(f"  ID: {user.id}, Username: {user.username}, Email: {user.email}")
        print()
        
        # Study Cards
        cards = StudyCard.query.all()
        print(f"STUDY CARDS ({len(cards)}):")
        for card in cards:
            print(f"  ID: {card.id}, Category: {card.category}")
            print(f"    Q: {card.question[:60]}...")
            print(f"    A: {card.answer[:60]}...")
        print()
        
        # Study Sessions
        sessions = StudySession.query.all()
        print(f"STUDY SESSIONS ({len(sessions)}):")
        for session in sessions:
            accuracy = session.calculate_accuracy()
            print(f"  ID: {session.id}, User: {session.user_id}, Accuracy: {accuracy}%")
            print(f"    Cards: {session.total_cards}, Correct: {session.correct_answers}")
        print()
        
        # Progress Records
        progress_records = Progress.query.all()
        print(f"PROGRESS RECORDS ({len(progress_records)}):")
        for progress in progress_records:
            success_rate = progress.calculate_success_rate()
            print(f"  User: {progress.user_id}, Card: {progress.card_id}")
            print(f"    Success Rate: {success_rate}%, Mastery: {progress.mastery_level}")

if __name__ == '__main__':
    view_database()