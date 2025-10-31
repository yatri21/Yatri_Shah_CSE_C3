from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from backend.models import db, User, StudyCard, StudySession, Progress, ChatMessage
from backend.chatbot import StudyBuddyChatbot
from datetime import datetime
import os





def create_app():
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_buddy.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Initialize chatbot
    chatbot = StudyBuddyChatbot()
    
    def init_sample_data():
        # Check if we already have data
        if StudyCard.query.first():
            return
        
        # Create sample users
        demo_user = User(username='demo', email='demo@example.com')
        demo_user.set_password('password')
        
        student_user = User(username='student', email='student@example.com')
        student_user.set_password('study123')
        
        db.session.add(demo_user)
        db.session.add(student_user)
        db.session.commit()
        
        # Create sample study cards
        sample_cards = [
            StudyCard(
                question="What is Python?",
                answer="A high-level, interpreted programming language known for its simplicity and readability",
                category="Programming"
            ),
            StudyCard(
                question="What is a variable in Python?",
                answer="A container that stores data values. Variables are created when you assign a value to them",
                category="Programming"
            ),
            StudyCard(
                question="What is a function?",
                answer="A reusable block of code that performs a specific task. Defined using the 'def' keyword",
                category="Programming"
            ),
            StudyCard(
                question="What is HTML?",
                answer="HyperText Markup Language - the standard markup language for creating web pages",
                category="Web Development"
            ),
            StudyCard(
                question="What is CSS?",
                answer="Cascading Style Sheets - used for styling and layout of web pages",
                category="Web Development"
            ),
            StudyCard(
                question="What is JavaScript?",
                answer="A programming language that enables interactive web pages and dynamic content",
                category="Web Development"
            ),
            StudyCard(
                question="What is a database?",
                answer="An organized collection of structured information, or data, typically stored electronically",
                category="Database"
            ),
            StudyCard(
                question="What is SQL?",
                answer="Structured Query Language - a programming language designed for managing data in relational databases",
                category="Database"
            )
        ]
        
        for card in sample_cards:
            db.session.add(card)
        
        # Create sample flashcard decks
        sample_decks = [
            FlashcardDeck(
                name="Python Programming",
                description="Essential Python concepts and syntax",
                category="Programming",
                user_id=1
            ),
            FlashcardDeck(
                name="Web Development Basics",
                description="HTML, CSS, and JavaScript fundamentals",
                category="Programming",
                user_id=1
            ),
            FlashcardDeck(
                name="Spanish Vocabulary",
                description="Common Spanish words and phrases",
                category="Languages",
                user_id=2
            )
        ]
        
        for deck in sample_decks:
            db.session.add(deck)
        
        db.session.commit()
        
        # Create sample flashcards
        sample_flashcards = [
            # Python deck cards
            Flashcard(deck_id=1, question="What is a variable in Python?", answer="A container that stores data values", difficulty="Easy"),
            Flashcard(deck_id=1, question="How do you create a list in Python?", answer="Using square brackets: my_list = [1, 2, 3]", difficulty="Easy"),
            Flashcard(deck_id=1, question="What is a function in Python?", answer="A reusable block of code that performs a specific task", difficulty="Medium"),
            Flashcard(deck_id=1, question="How do you handle exceptions in Python?", answer="Using try/except blocks", difficulty="Medium"),
            
            # Web development deck cards
            Flashcard(deck_id=2, question="What does HTML stand for?", answer="HyperText Markup Language", difficulty="Easy"),
            Flashcard(deck_id=2, question="How do you center a div with CSS?", answer="Use margin: 0 auto; or display: flex; justify-content: center;", difficulty="Medium"),
            Flashcard(deck_id=2, question="What is the DOM?", answer="Document Object Model - a programming interface for HTML documents", difficulty="Hard"),
            
            # Spanish deck cards
            Flashcard(deck_id=3, question="How do you say 'Hello' in Spanish?", answer="Hola", difficulty="Easy"),
            Flashcard(deck_id=3, question="What is 'Thank you' in Spanish?", answer="Gracias", difficulty="Easy"),
            Flashcard(deck_id=3, question="How do you say 'Good morning' in Spanish?", answer="Buenos días", difficulty="Easy")
        ]
        
        for flashcard in sample_flashcards:
            db.session.add(flashcard)
        
        db.session.commit()
    
    # Create tables and sample data
    with app.app_context():
        db.create_all()
        init_sample_data()
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('landing.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('dashboard'))
            flash('Invalid username or password')
        
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            # Check if user exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return render_template('register.html')
            
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html', user=current_user)
    
    @app.route('/study')
    @login_required
    def study():
        return render_template('study.html')
    
    @app.route('/chat')
    @login_required
    def chat_page():
        return render_template('chat.html')
    

    
    @app.route('/api/cards')
    def get_cards():
        cards = StudyCard.query.filter_by(is_active=True).all()
        return jsonify([card.to_dict() for card in cards])
    
    @app.route('/api/cards/<int:card_id>')
    def get_card(card_id):
        card = StudyCard.query.get(card_id)
        if card and card.is_active:
            return jsonify(card.to_dict())
        return jsonify({'error': 'Card not found'}), 404
    
    @app.route('/api/progress', methods=['POST'])
    @login_required
    def update_progress():
        data = request.get_json()
        
        # Create or update study session
        session_record = StudySession(
            user_id=current_user.id,
            total_cards=data.get('total', 0),
            correct_answers=data.get('correct', 0),
            incorrect_answers=data.get('incorrect', 0),
            session_duration=data.get('duration', 0)
        )
        
        db.session.add(session_record)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Progress updated'})
    
    @app.route('/api/chat', methods=['POST'])
    @login_required
    def chat_with_bot():
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get user context for personalized responses
        user_stats = get_user_stats_data(current_user.id)
        
        # Get chatbot response
        bot_response = chatbot.get_response(user_message, user_stats)
        
        # Save chat message to database
        chat_message = ChatMessage(
            user_id=current_user.id,
            message=user_message,
            response=bot_response['response'],
            message_type=bot_response.get('type', 'general')
        )
        
        db.session.add(chat_message)
        db.session.commit()
        
        return jsonify({
            'response': bot_response['response'],
            'type': bot_response.get('type', 'general'),
            'timestamp': chat_message.timestamp.isoformat()
        })
    
    @app.route('/api/chat/history')
    @login_required
    def get_chat_history():
        messages = ChatMessage.query.filter_by(user_id=current_user.id)\
                                  .order_by(ChatMessage.timestamp.desc())\
                                  .limit(50).all()
        
        return jsonify([msg.to_dict() for msg in reversed(messages)])
    
    @app.route('/api/chat/generate-question', methods=['POST'])
    @login_required
    def generate_practice_question():
        data = request.get_json()
        topic = data.get('topic', 'general')
        
        question_data = chatbot.generate_study_question(topic)
        
        return jsonify(question_data)
    

    
    @app.route('/api/user/stats')
    @login_required
    def get_user_stats():
        return jsonify(get_user_stats_data(current_user.id))
    
    def calculate_study_streak(user_id):
        # Simplified streak calculation
        sessions = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.start_time.desc()).all()
        if not sessions:
            return 0
        
        # For simplicity, return number of sessions in last 7 days
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_sessions = [s for s in sessions if s.start_time >= week_ago]
        return len(recent_sessions)

    def get_user_stats_data(user_id):
        # Get user statistics
        sessions = StudySession.query.filter_by(user_id=user_id).all()
        
        total_sessions = len(sessions)
        total_cards_studied = sum(s.total_cards for s in sessions)
        total_correct = sum(s.correct_answers for s in sessions)
        total_incorrect = sum(s.incorrect_answers for s in sessions)
        
        accuracy = 0
        if total_cards_studied > 0:
            accuracy = round((total_correct / total_cards_studied) * 100, 2)
        
        # Calculate streak (simplified - consecutive days with sessions)
        streak = calculate_study_streak(user_id)
        
        return {
            'total_sessions': total_sessions,
            'cards_studied': total_cards_studied,
            'accuracy': accuracy,
            'streak': streak,
            'total_correct': total_correct,
            'total_incorrect': total_incorrect
        }
    
    def init_sample_data():
        # Check if we already have data
        if StudyCard.query.first():
            return
        
        # Create sample users
        demo_user = User(username='demo', email='demo@example.com')
        demo_user.set_password('password')
        
        student_user = User(username='student', email='student@example.com')
        student_user.set_password('study123')
        
        db.session.add(demo_user)
        db.session.add(student_user)
        db.session.commit()
        
        # Create sample study cards
        sample_cards = [
            StudyCard(
                question="What is Python?",
                answer="A high-level, interpreted programming language known for its simplicity and readability",
                category="Programming"
            ),
            StudyCard(
                question="What is a variable in Python?",
                answer="A container that stores data values. Variables are created when you assign a value to them",
                category="Programming"
            ),
            StudyCard(
                question="What is a function?",
                answer="A reusable block of code that performs a specific task. Defined using the 'def' keyword",
                category="Programming"
            ),
            StudyCard(
                question="What is HTML?",
                answer="HyperText Markup Language - the standard markup language for creating web pages",
                category="Web Development"
            ),
            StudyCard(
                question="What is CSS?",
                answer="Cascading Style Sheets - used for styling and layout of web pages",
                category="Web Development"
            ),
            StudyCard(
                question="What is JavaScript?",
                answer="A programming language that enables interactive web pages and dynamic content",
                category="Web Development"
            ),
            StudyCard(
                question="What is a database?",
                answer="An organized collection of structured information, or data, typically stored electronically",
                category="Database"
            ),
            StudyCard(
                question="What is SQL?",
                answer="Structured Query Language - a programming language designed for managing data in relational databases",
                category="Database"
            )
        ]
        
        for card in sample_cards:
            db.session.add(card)
        
        db.session.commit()
    
    return app