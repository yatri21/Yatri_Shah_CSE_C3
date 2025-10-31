import openai
import os
from typing import Dict, List
import json

class StudyBuddyChatbot:
    def __init__(self):
        # For demo purposes, we'll use a simple rule-based system
        # In production, you'd use OpenAI API or another AI service
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
        
        # Predefined responses for common study topics
        self.knowledge_base = {
            'python': {
                'keywords': ['python', 'programming', 'code', 'variable', 'function', 'loop', 'list', 'dictionary'],
                'responses': [
                    "Python is a versatile programming language! What specific Python concept would you like help with?",
                    "I can help you with Python basics like variables, functions, loops, and data structures.",
                    "Python is great for beginners! Would you like me to explain any particular concept?"
                ]
            },
            'web': {
                'keywords': ['html', 'css', 'javascript', 'web', 'website', 'frontend', 'backend'],
                'responses': [
                    "Web development involves HTML for structure, CSS for styling, and JavaScript for interactivity.",
                    "I can help you understand web technologies! What aspect interests you most?",
                    "Building websites is exciting! Are you working on frontend or backend development?"
                ]
            },
            'database': {
                'keywords': ['database', 'sql', 'data', 'table', 'query', 'mysql', 'sqlite'],
                'responses': [
                    "Databases store and organize data efficiently. SQL is the language used to interact with them.",
                    "I can help you understand database concepts like tables, queries, and relationships.",
                    "Database design is crucial for applications. What database topic interests you?"
                ]
            },
            'study': {
                'keywords': ['study', 'learn', 'practice', 'quiz', 'flashcard', 'memory', 'review'],
                'responses': [
                    "Great question about studying! I recommend using spaced repetition and active recall techniques.",
                    "Effective studying involves regular practice, breaking topics into chunks, and testing yourself.",
                    "I can help you create a study plan or explain concepts you're struggling with!"
                ]
            }
        }
        
        self.general_responses = [
            "I'm here to help you with your studies! What would you like to learn about?",
            "That's an interesting question! Can you provide more details so I can help better?",
            "I'm your study buddy! Feel free to ask me about programming, web development, databases, or study techniques.",
            "Let me help you with that! What specific topic or concept would you like to explore?",
            "Great question! I can assist with explanations, create practice questions, or help clarify concepts."
        ]

    def get_response(self, message: str, user_context: Dict = None) -> Dict:
        """
        Generate a response to the user's message
        """
        message_lower = message.lower()
        
        # Try to use Gemini AI if available
        if self.model:
            try:
                return self._get_gemini_response(message, user_context)
            except Exception as e:
                print(f"Gemini AI error: {e}")
                # Fall back to rule-based system
        
        # Rule-based response system
        return self._get_rule_based_response(message_lower, user_context)
    
    def _get_gemini_response(self, message: str, user_context: Dict = None) -> Dict:
        """
        Get response from Google Gemini AI
        """
        # Create context-aware prompt
        context_info = ""
        if user_context:
            context_info = f"""
            User Context:
            - Study Sessions: {user_context.get('total_sessions', 0)}
            - Cards Studied: {user_context.get('cards_studied', 0)}
            - Accuracy Rate: {user_context.get('accuracy', 0)}%
            - Study Streak: {user_context.get('streak', 0)} days
            """
        
        system_prompt = f"""You are a helpful study assistant for a learning platform called Study Buddy. 
        You help students learn programming, web development, databases, and general study techniques.
        Keep responses concise (under 150 words), encouraging, and educational. 
        If asked about topics outside of studying/learning, gently redirect to educational topics.
        
        {context_info}
        
        Student Question: {message}
        
        Provide a helpful, encouraging response that assists with their learning."""
        
        try:
            response = self.model.generate_content(system_prompt)
            
            return {
                'response': response.text.strip(),
                'type': 'gemini_ai',
                'confidence': 0.95
            }
        except Exception as e:
            raise e
    
    def _get_rule_based_response(self, message_lower: str, user_context: Dict = None) -> Dict:
        """
        Get response using rule-based system
        """
        import random
        
        # Check for specific topics
        for topic, data in self.knowledge_base.items():
            if any(keyword in message_lower for keyword in data['keywords']):
                response = random.choice(data['responses'])
                return {
                    'response': response,
                    'type': 'rule_based',
                    'topic': topic,
                    'confidence': 0.8
                }
        
        # Check for specific question patterns
        if any(word in message_lower for word in ['what', 'how', 'why', 'explain', 'help']):
            if 'study' in message_lower or 'learn' in message_lower:
                response = "I'd be happy to help you study! What specific topic or concept would you like to work on?"
            elif 'quiz' in message_lower or 'test' in message_lower:
                response = "I can help you practice! Try using the study cards feature, or ask me to explain any concept you're unsure about."
            else:
                response = random.choice(self.general_responses)
        elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            response = "Hello! I'm your Study Buddy assistant. I'm here to help you learn and practice. What would you like to study today?"
        elif any(word in message_lower for word in ['thanks', 'thank you', 'appreciate']):
            response = "You're welcome! I'm always here to help with your studies. Keep up the great work!"
        else:
            response = random.choice(self.general_responses)
        
        return {
            'response': response,
            'type': 'rule_based',
            'confidence': 0.6
        }
    
    def generate_study_question(self, topic: str) -> Dict:
        """
        Generate a practice question for a given topic
        """
        questions = {
            'python': [
                "What is the difference between a list and a tuple in Python?",
                "How do you create a function in Python?",
                "What is a Python dictionary and how do you use it?",
                "Explain the concept of loops in Python."
            ],
            'web': [
                "What is the difference between HTML and CSS?",
                "How do you make a website responsive?",
                "What is the DOM in web development?",
                "Explain the difference between frontend and backend."
            ],
            'database': [
                "What is a primary key in a database?",
                "How do you write a SELECT query in SQL?",
                "What is database normalization?",
                "Explain the difference between SQL and NoSQL databases."
            ]
        }
        
        import random
        if topic.lower() in questions:
            question = random.choice(questions[topic.lower()])
            return {
                'question': question,
                'topic': topic,
                'type': 'practice_question'
            }
        
        return {
            'question': "What would you like to learn more about?",
            'topic': 'general',
            'type': 'general_question'
        }