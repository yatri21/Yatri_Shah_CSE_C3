from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Gemini API configuration
GEMINI_API_KEY = "AIzaSyCTtT2K81P2odu47dm0or2QUDV_79iS8UY"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# Conversation history storage (last 10 messages)
conversation_history = []

def add_to_history(role, content):
    """Add message to history and maintain 10-message limit"""
    conversation_history.append({
        "role": role,
        "parts": [{"text": content}]
    })
    # Keep only last 10 messages
    if len(conversation_history) > 10:
        conversation_history.pop(0)

def clear_history():
    """Reset conversation history"""
    global conversation_history
    conversation_history = []

def call_gemini_api(message):
    """Send request to Gemini API with conversation context"""
    try:
        # Add current user message to history
        add_to_history("user", message)
        
        # Prepare request payload with full conversation history
        payload = {
            "contents": conversation_history
        }
        
        print(f"Sending request to Gemini API with {len(conversation_history)} messages")
        
        # Make API request
        response = requests.post(
            GEMINI_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Check for API errors
        if response.status_code != 200:
            error_msg = f"API Error: {response.status_code}"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except:
                pass
            return None, error_msg
        
        # Extract response text
        result = response.json()
        if "candidates" in result and len(result["candidates"]) > 0:
            ai_response = result["candidates"][0]["content"]["parts"][0]["text"]
            # Add AI response to history
            add_to_history("model", ai_response)
            return ai_response, None
        else:
            return None, "No response from API"
            
    except requests.exceptions.Timeout:
        return None, "Request timeout"
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Invalid request format"}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Call Gemini API
        ai_response, error = call_gemini_api(user_message)
        
        if error:
            return jsonify({"error": error}), 500
        
        return jsonify({"response": ai_response})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear():
    """Clear conversation history"""
    try:
        clear_history()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def serve_index():
    """Serve the frontend HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🚀 Server starting on http://localhost:{port}")
    print(f"📝 Open your browser and navigate to http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
