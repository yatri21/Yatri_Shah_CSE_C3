class StudySession {
    constructor() {
        this.cards = [];
        this.currentCardIndex = 0;
        this.stats = { correct: 0, incorrect: 0, total: 0 };
        this.timer = {
            startTime: null,
            elapsedTime: 0,
            isRunning: false,
            interval: null
        };
        this.performanceHistory = [];
        this.charts = {};
        this.init();
    }

    async init() {
        await this.loadCards();
        this.displayCard();
        this.updateStats();
        this.initializeCharts();
        this.startTimer();
    }

    async loadCards() {
        try {
            // Check if we have a specific deck ID
            const deckId = window.deckId;
            let response;
            
            if (deckId) {
                response = await fetch(`/api/flashcard-decks/${deckId}/cards`);
            } else {
                response = await fetch('/api/cards');
            }
            
            this.cards = await response.json();
            
            if (this.cards.length === 0) {
                this.showEmptyState();
                return;
            }
        } catch (error) {
            console.error('Failed to load cards:', error);
            this.cards = [
                {id: 1, question: "What is Python?", answer: "A high-level programming language known for its simplicity and readability"},
                {id: 2, question: "What is Flask?", answer: "A lightweight web framework for Python that's easy to learn and use"},
                {id: 3, question: "What is HTML?", answer: "HyperText Markup Language - the standard markup language for web pages"},
                {id: 4, question: "What is CSS?", answer: "Cascading Style Sheets - used for styling and layout of web pages"},
                {id: 5, question: "What is JavaScript?", answer: "A programming language that enables interactive web pages and dynamic content"},
                {id: 6, question: "What is a function?", answer: "A reusable block of code that performs a specific task"}
            ];
        }
    }

    showEmptyState() {
        const studyCard = document.getElementById('studyCard');
        studyCard.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-layer-group"></i>
                <h3>No Cards in This Deck</h3>
                <p>This deck doesn't have any flashcards yet.</p>
                <a href="/flashcards" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Add Cards to Deck
                </a>
            </div>
        `;
        
        // Hide controls
        document.querySelector('.study-controls').style.display = 'none';
        document.querySelector('.study-modes').style.display = 'none';
        document.querySelector('.study-stats').style.display = 'none';
        document.querySelector('.progress-charts').style.display = 'none';
    }

    displayCard() {
        if (this.cards.length === 0) return;
        
        const card = this.cards[this.currentCardIndex];
        document.getElementById('questionText').textContent = card.question;
        document.getElementById('answerText').textContent = card.answer;
        document.getElementById('cardCounter').textContent = `${this.currentCardIndex + 1} / ${this.cards.length}`;
        
        this.showQuestion();
        this.updateProgress();
        this.updateNavigationButtons();
    }

    showQuestion() {
        document.getElementById('questionSide').style.display = 'block';
        document.getElementById('answerSide').style.display = 'none';
    }

    showAnswer() {
        document.getElementById('questionSide').style.display = 'none';
        document.getElementById('answerSide').style.display = 'block';
    }

    nextCard() {
        if (this.currentCardIndex < this.cards.length - 1) {
            this.currentCardIndex++;
            this.displayCard();
        }
    }

    previousCard() {
        if (this.currentCardIndex > 0) {
            this.currentCardIndex--;
            this.displayCard();
        }
    }

    markCorrect() {
        this.stats.correct++;
        this.stats.total++;
        this.updateStats();
        this.saveProgress();
        this.updateCardStats(true);
        
        if (this.currentCardIndex < this.cards.length - 1) {
            setTimeout(() => this.nextCard(), 500);
        } else {
            this.showSessionComplete();
        }
    }

    markIncorrect() {
        this.stats.incorrect++;
        this.stats.total++;
        this.updateStats();
        this.saveProgress();
        this.updateCardStats(false);
        
        if (this.currentCardIndex < this.cards.length - 1) {
            setTimeout(() => this.nextCard(), 500);
        } else {
            this.showSessionComplete();
        }
    }

    async updateCardStats(isCorrect) {
        const currentCard = this.cards[this.currentCardIndex];
        if (!currentCard || !currentCard.deck_id) return;

        try {
            await fetch(`/api/flashcards/${currentCard.id}/study`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ is_correct: isCorrect })
            });
        } catch (error) {
            console.error('Failed to update card stats:', error);
        }
    }

    updateProgress() {
        const percentage = this.cards.length > 0 ? ((this.currentCardIndex + 1) / this.cards.length) * 100 : 0;
        
        // Update circular progress
        const circle = document.getElementById('progressCircle');
        const circumference = 2 * Math.PI * 34;
        const offset = circumference - (percentage / 100) * circumference;
        circle.style.strokeDasharray = circumference;
        circle.style.strokeDashoffset = offset;
        
        document.getElementById('progressPercentage').textContent = `${Math.round(percentage)}%`;
        document.getElementById('progressText').textContent = `${Math.round(percentage)}% Complete`;
        
        this.updateCharts();
    }

    updateStats() {
        document.getElementById('correctCount').textContent = this.stats.correct;
        document.getElementById('incorrectCount').textContent = this.stats.incorrect;
        
        const accuracy = this.stats.total > 0 ? Math.round((this.stats.correct / this.stats.total) * 100) : 0;
        document.getElementById('accuracyRate').textContent = `${accuracy}%`;
        
        // Update total time
        document.getElementById('totalTime').textContent = this.formatTime(this.timer.elapsedTime);
        
        // Add to performance history
        if (this.stats.total > 0) {
            this.performanceHistory.push({
                cardNumber: this.stats.total,
                accuracy: accuracy,
                timeSpent: this.timer.elapsedTime
            });
        }
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        
        prevBtn.disabled = this.currentCardIndex === 0;
        nextBtn.disabled = this.currentCardIndex === this.cards.length - 1;
    }

    async saveProgress() {
        try {
            const progressData = {
                correct: this.stats.correct,
                incorrect: this.stats.incorrect,
                total: this.stats.total,
                duration: this.timer.elapsedTime
            };
            
            await fetch('/api/progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(progressData)
            });
        } catch (error) {
            console.error('Failed to save progress:', error);
        }
    }

    startQuiz() {
        this.cards = this.shuffleArray([...this.cards]);
        this.currentCardIndex = 0;
        this.stats = { correct: 0, incorrect: 0, total: 0 };
        this.displayCard();
        this.updateStats();
        
        // Show quiz mode notification
        this.showNotification('Quiz mode activated! Cards have been shuffled.', 'info');
    }

    resetSession() {
        this.currentCardIndex = 0;
        this.stats = { correct: 0, incorrect: 0, total: 0 };
        this.displayCard();
        this.updateStats();
        
        this.showNotification('Session reset successfully!', 'success');
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    showSessionComplete() {
        const accuracy = Math.round((this.stats.correct / this.stats.total) * 100);
        let message = `Session Complete!\n\nCorrect: ${this.stats.correct}\nIncorrect: ${this.stats.incorrect}\nAccuracy: ${accuracy}%`;
        
        if (accuracy >= 90) {
            message += '\n\n🎉 Excellent work!';
        } else if (accuracy >= 70) {
            message += '\n\n👍 Good job!';
        } else {
            message += '\n\n💪 Keep practicing!';
        }
        
        alert(message);
    }

    // Timer Methods
    startTimer() {
        if (!this.timer.isRunning) {
            this.timer.startTime = Date.now() - this.timer.elapsedTime;
            this.timer.isRunning = true;
            this.timer.interval = setInterval(() => {
                this.timer.elapsedTime = Date.now() - this.timer.startTime;
                this.updateTimerDisplay();
            }, 1000);
            
            const timerBtn = document.getElementById('timerBtn');
            timerBtn.innerHTML = '<i class="fas fa-pause"></i>';
        }
    }

    pauseTimer() {
        if (this.timer.isRunning) {
            clearInterval(this.timer.interval);
            this.timer.isRunning = false;
            
            const timerBtn = document.getElementById('timerBtn');
            timerBtn.innerHTML = '<i class="fas fa-play"></i>';
        }
    }

    resetTimer() {
        clearInterval(this.timer.interval);
        this.timer.elapsedTime = 0;
        this.timer.isRunning = false;
        this.updateTimerDisplay();
        
        const timerBtn = document.getElementById('timerBtn');
        timerBtn.innerHTML = '<i class="fas fa-play"></i>';
    }

    toggleTimer() {
        if (this.timer.isRunning) {
            this.pauseTimer();
        } else {
            this.startTimer();
        }
    }

    updateTimerDisplay() {
        const timeString = this.formatTime(this.timer.elapsedTime);
        document.getElementById('timerDisplay').textContent = timeString;
    }

    formatTime(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    // Chart Methods
    initializeCharts() {
        this.initProgressChart();
        this.initPerformanceChart();
    }

    initProgressChart() {
        const ctx = document.getElementById('progressChart').getContext('2d');
        this.charts.progress = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Correct', 'Incorrect', 'Remaining'],
                datasets: [{
                    data: [0, 0, this.cards.length],
                    backgroundColor: ['#4CAF50', '#f44336', '#e0e0e0'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    initPerformanceChart() {
        const ctx = document.getElementById('performanceChart').getContext('2d');
        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Accuracy %',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Card Number'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    updateCharts() {
        // Update progress chart
        const remaining = this.cards.length - this.stats.total;
        this.charts.progress.data.datasets[0].data = [
            this.stats.correct,
            this.stats.incorrect,
            remaining
        ];
        this.charts.progress.update();

        // Update performance chart
        if (this.performanceHistory.length > 0) {
            const labels = this.performanceHistory.map(h => `Card ${h.cardNumber}`);
            const accuracyData = this.performanceHistory.map(h => h.accuracy);
            
            this.charts.performance.data.labels = labels;
            this.charts.performance.data.datasets[0].data = accuracyData;
            this.charts.performance.update();
        }
    }

    showNotification(message, type = 'info') {
        // Simple notification - in a real app you'd use a proper notification system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Global functions for HTML onclick events
let studySession;

function showAnswer() {
    studySession.showAnswer();
}

function nextCard() {
    studySession.nextCard();
}

function previousCard() {
    studySession.previousCard();
}

function markCorrect() {
    studySession.markCorrect();
}

function markIncorrect() {
    studySession.markIncorrect();
}

function startQuiz() {
    studySession.startQuiz();
}

function resetSession() {
    studySession.resetSession();
}

function toggleTimer() {
    studySession.toggleTimer();
}

function resetTimer() {
    studySession.resetTimer();
}

// Initialize study session when page loads
document.addEventListener('DOMContentLoaded', () => {
    studySession = new StudySession();
});

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);