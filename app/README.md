# Study Buddy

A full-stack study platform with Python Flask backend, SQLite database, and interactive frontend.

## Project Structure
```
├── backend/
│   ├── app.py         # Flask application
│   └── models.py      # Database models
├── frontend/          # Templates and static files
├── requirements.txt   # Python dependencies
├── run.py            # Application entry point
├── init_db.py        # Database initialization
└── view_db.py        # Database viewer (debug)
```

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Initialize database: `python init_db.py`
3. Run the server: `python run.py`
4. Open http://localhost:5000

## Features
- **User Authentication** - Register/Login with secure password hashing
- **SQLite Database** - Persistent data storage
- **Interactive Study Cards** - Flip cards with questions and answers
- **Progress Tracking** - Real-time statistics and performance analytics
- **Study Sessions** - Timed sessions with accuracy tracking
- **Dark/Light Theme** - Toggle between themes
- **Responsive Design** - Works on desktop and mobile

## Demo Accounts
- Username: `demo`, Password: `password`
- Username: `student`, Password: `study123`

## Database
The app uses SQLite database (`study_buddy.db`) with the following tables:
- **Users** - User accounts and authentication
- **StudyCards** - Questions and answers with categories
- **StudySessions** - Session history and performance
- **Progress** - Individual card progress and mastery levels

## AI Assistant Setup (Optional)
To enable the full AI-powered chatbot with Google Gemini:

1. Get a Google AI API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the environment variable:
   ```bash
   # Windows
   set GEMINI_API_KEY=your_api_key_here
   
   # Linux/Mac
   export GEMINI_API_KEY=your_api_key_here
   ```
3. Restart the application

Without an API key, the chatbot uses a rule-based system with predefined responses.

## Development
- View database contents: `python view_db.py`
- Reset database: `python init_db.py`