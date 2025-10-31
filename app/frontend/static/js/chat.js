class ChatInterface {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.isLoading = false;
        
        this.init();
    }

    async init() {
        await this.checkAIStatus();
        await this.loadChatHistory();
        await this.loadUserStats();
        this.scrollToBottom();
    }

    async checkAIStatus() {
        try {
            const response = await fetch('/api/chat/status');
            const status = await response.json();
            
            const statusIcon = document.getElementById('statusIcon');
            const statusText = document.getElementById('statusText');
            
            if (status.ai_available) {
                statusIcon.className = 'fas fa-circle status-online';
                statusText.textContent = `${status.ai_type} AI - Online`;
            } else {
                statusIcon.className = 'fas fa-circle status-offline';
                statusText.textContent = `${status.ai_type} - Offline (Set GEMINI_API_KEY for full AI)`;
            }
        } catch (error) {
            console.error('Failed to check AI status:', error);
        }
    }

    async loadChatHistory() {
        try {
            const response = await fetch('/api/chat/history');
            const messages = await response.json();
            
            // Clear existing messages except welcome message
            const welcomeMessage = this.messagesContainer.querySelector('.bot-message');
            this.messagesContainer.innerHTML = '';
            if (welcomeMessage) {
                this.messagesContainer.appendChild(welcomeMessage);
            }
            
            // Add chat history
            messages.forEach(msg => {
                this.addUserMessage(msg.message, false);
                this.addBotMessage(msg.response, false);
            });
            
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    async loadUserStats() {
        try {
            const response = await fetch('/api/user/stats');
            const stats = await response.json();
            
            document.getElementById('sidebarStreak').textContent = `${stats.streak} days`;
            document.getElementById('sidebarCards').textContent = stats.cards_studied;
            document.getElementById('sidebarAccuracy').textContent = `${stats.accuracy}%`;
        } catch (error) {
            console.error('Failed to load user stats:', error);
        }
    }

    async sendMessage(message = null) {
        const messageText = message || this.chatInput.value.trim();
        
        if (!messageText || this.isLoading) return;

        // Add user message to chat
        this.addUserMessage(messageText);
        
        // Clear input
        this.chatInput.value = '';
        
        // Show loading
        this.setLoading(true);
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.addBotMessage(data.response);
            } else {
                this.addBotMessage('Sorry, I encountered an error. Please try again.');
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addBotMessage('Sorry, I\'m having trouble connecting. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    addUserMessage(message, scroll = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'user-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(message)}</p>
            </div>
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
        `;
        
        this.messagesContainer.appendChild(messageDiv);
        if (scroll) this.scrollToBottom();
    }

    addBotMessage(message, scroll = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'bot-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>${this.formatBotMessage(message)}</p>
            </div>
        `;
        
        this.messagesContainer.appendChild(messageDiv);
        if (scroll) this.scrollToBottom();
    }

    formatBotMessage(message) {
        // Simple formatting for bot messages
        return this.escapeHtml(message)
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setLoading(loading) {
        this.isLoading = loading;
        this.sendButton.disabled = loading;
        
        if (loading) {
            this.sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.addTypingIndicator();
        } else {
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
            this.removeTypingIndicator();
        }
    }

    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'bot-message typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    async generatePracticeQuestion() {
        try {
            const response = await fetch('/api/chat/generate-question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic: 'general' })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.addBotMessage(`Here's a practice question for you: ${data.question}`);
            }
        } catch (error) {
            console.error('Failed to generate question:', error);
            this.addBotMessage('Sorry, I couldn\'t generate a practice question right now.');
        }
    }
}

// Global functions for HTML onclick events
let chatInterface;

function sendMessage() {
    chatInterface.sendMessage();
}

function sendQuickMessage(message) {
    chatInterface.sendMessage(message);
}

function generateQuestion() {
    chatInterface.generatePracticeQuestion();
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Initialize chat interface when page loads
document.addEventListener('DOMContentLoaded', () => {
    chatInterface = new ChatInterface();
});