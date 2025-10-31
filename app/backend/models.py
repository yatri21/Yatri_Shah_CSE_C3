from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    study_sessions = db.relationship('StudySession', backref='user', lazy=True)
    progress_records = db.relationship('Progress', backref='user', lazy=True)
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True)
    flashcard_decks = db.relationship('FlashcardDeck', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class StudyCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='General')
    difficulty = db.Column(db.String(20), default='Medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }

    def __repr__(self):
        return f'<StudyCard {self.id}: {self.question[:50]}...>'

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_cards = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    incorrect_answers = db.Column(db.Integer, default=0)
    session_duration = db.Column(db.Integer)  # in seconds
    
    def calculate_accuracy(self):
        if self.total_cards > 0:
            return round((self.correct_answers / self.total_cards) * 100, 2)
        return 0

    def __repr__(self):
        return f'<StudySession {self.id} - User {self.user_id}>'

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('study_card.id'), nullable=False)
    correct_count = db.Column(db.Integer, default=0)
    incorrect_count = db.Column(db.Integer, default=0)
    last_reviewed = db.Column(db.DateTime, default=datetime.utcnow)
    mastery_level = db.Column(db.String(20), default='Beginner')  # Beginner, Intermediate, Advanced, Mastered
    
    # Relationship
    card = db.relationship('StudyCard', backref='progress_records')

    def calculate_success_rate(self):
        total = self.correct_count + self.incorrect_count
        if total > 0:
            return round((self.correct_count / total) * 100, 2)
        return 0

    def update_mastery_level(self):
        success_rate = self.calculate_success_rate()
        total_attempts = self.correct_count + self.incorrect_count
        
        if success_rate >= 90 and total_attempts >= 5:
            self.mastery_level = 'Mastered'
        elif success_rate >= 75 and total_attempts >= 3:
            self.mastery_level = 'Advanced'
        elif success_rate >= 60 and total_attempts >= 2:
            self.mastery_level = 'Intermediate'
        else:
            self.mastery_level = 'Beginner'

    def __repr__(self):
        return f'<Progress User:{self.user_id} Card:{self.card_id}>'

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message_type = db.Column(db.String(20), default='general')  # general, study_help, quiz, explanation
    
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'response': self.response,
            'timestamp': self.timestamp.isoformat(),
            'type': self.message_type
        }

    def __repr__(self):
        return f'<ChatMessage {self.id} - User {self.user_id}>'

class FlashcardDeck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), default='General')
    
    # Relationships
    flashcards = db.relationship('Flashcard', backref='deck', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'category': self.category,
            'card_count': len(self.flashcards),
            'is_public': self.is_public
        }

    def __repr__(self):
        return f'<FlashcardDeck {self.id}: {self.name}>'

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('flashcard_deck.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    hint = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default='Medium')  # Easy, Medium, Hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Study statistics
    times_studied = db.Column(db.Integer, default=0)
    times_correct = db.Column(db.Integer, default=0)
    last_studied = db.Column(db.DateTime)
    
    def to_dict(self):
        success_rate = 0
        if self.times_studied > 0:
            success_rate = round((self.times_correct / self.times_studied) * 100, 2)
            
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'question': self.question,
            'answer': self.answer,
            'hint': self.hint,
            'difficulty': self.difficulty,
            'times_studied': self.times_studied,
            'times_correct': self.times_correct,
            'success_rate': success_rate,
            'last_studied': self.last_studied.isoformat() if self.last_studied else None,
            'created_at': self.created_at.isoformat()
        }
    
    def update_study_stats(self, is_correct):
        self.times_studied += 1
        if is_correct:
            self.times_correct += 1
        self.last_studied = datetime.utcnow()

    def __repr__(self):
        return f'<Flashcard {self.id}: {self.question[:30]}...>'