class StudyApp {
    constructor() {
        this.cards = [];
        this.currentCardIndex = 0;
        this.progress = { correct: 0, total: 0 };
        this.init();
    }

    async init() {
        await this.loadCards();
        this.displayCard();
        this.updateProgress();
    }

    async loadCards() {
        try {
            const response = await fetch('/api/cards');
            this.cards = await response.json();
        } catch (error) {
            console.error('Failed to load cards:', error);
            // Fallback data
            this.cards = [
                {id: 1, question: "What is JavaScript?", answer: "A programming language for web development"},
                {id: 2, question: "What is a function?", answer: "A reusable block of code that performs a task"}
            ];
        }
    }

    displayCard() {
        if (this.cards.length === 0) return;
        
        const card = this.cards[this.currentCardIndex];
        document.getElementById('questionText').textContent = card.question;
        document.getElementById('answerText').textContent = card.answer;
        document.getElementById('cardCounter').textContent = `${this.currentCardIndex + 1} / ${this.cards.length}`;
        
        // Reset to question side
        this.showQuestion();
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
        this.progress.correct++;
        this.progress.total++;
        this.updateProgress();
        this.saveProgress();
        this.nextCard();
    }

    markIncorrect() {
        this.progress.total++;
        this.updateProgress();
        this.saveProgress();
        this.nextCard();
    }

    updateProgress() {
        const percentage = this.progress.total > 0 ? (this.progress.correct / this.progress.total) * 100 : 0;
        document.getElementById('progressFill').style.width = `${Math.min(percentage, 100)}%`;
    }

    async saveProgress() {
        try {
            await fetch('/api/progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.progress)
            });
        } catch (error) {
            console.error('Failed to save progress:', error);
        }
    }

    startQuiz() {
        // Shuffle cards for quiz mode
        this.cards = this.shuffleArray([...this.cards]);
        this.currentCardIndex = 0;
        this.progress = { correct: 0, total: 0 };
        this.displayCard();
        this.updateProgress();
        alert('Quiz mode started! Cards have been shuffled.');
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }
}

// Global functions for HTML onclick events
let app;

function showAnswer() {
    app.showAnswer();
}

function nextCard() {
    app.nextCard();
}

function previousCard() {
    app.previousCard();
}

function markCorrect() {
    app.markCorrect();
}

function markIncorrect() {
    app.markIncorrect();
}

function startQuiz() {
    app.startQuiz();
}

// Initialize app when page loads
document.addEventListener('DOMContentLoaded', () => {
    app = new StudyApp();
});