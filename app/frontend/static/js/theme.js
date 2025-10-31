class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.createThemeToggle();
        this.updateToggleIcon();
    }

    createThemeToggle() {
        // Check if toggle already exists
        if (document.getElementById('themeToggle')) return;

        const toggle = document.createElement('button');
        toggle.id = 'themeToggle';
        toggle.className = 'theme-toggle';
        toggle.innerHTML = '<i class="fas fa-moon"></i>';
        toggle.title = 'Toggle Dark Theme';
        toggle.addEventListener('click', () => this.toggleTheme());

        // Add to navigation
        const navLinks = document.querySelector('.nav-links');
        if (navLinks) {
            navLinks.insertBefore(toggle, navLinks.firstChild);
        }
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        this.updateToggleIcon();
        localStorage.setItem('theme', this.currentTheme);
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: this.currentTheme } 
        }));
    }

    applyTheme(theme) {
        const body = document.body;
        
        if (theme === 'dark') {
            body.classList.add('dark-theme');
        } else {
            body.classList.remove('dark-theme');
        }

        // Update meta theme-color for mobile browsers
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        metaThemeColor.content = theme === 'dark' ? '#1a1a1a' : '#667eea';
    }

    updateToggleIcon() {
        const toggle = document.getElementById('themeToggle');
        if (!toggle) return;

        const icon = toggle.querySelector('i');
        if (this.currentTheme === 'dark') {
            icon.className = 'fas fa-sun';
            toggle.title = 'Switch to Light Theme';
        } else {
            icon.className = 'fas fa-moon';
            toggle.title = 'Switch to Dark Theme';
        }
    }

    getCurrentTheme() {
        return this.currentTheme;
    }

    // Method to programmatically set theme
    setTheme(theme) {
        if (theme === 'light' || theme === 'dark') {
            this.currentTheme = theme;
            this.applyTheme(theme);
            this.updateToggleIcon();
            localStorage.setItem('theme', theme);
        }
    }

    // Auto-detect system preference
    detectSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    // Enable auto theme switching based on system preference
    enableAutoTheme() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        const handleChange = (e) => {
            const systemTheme = e.matches ? 'dark' : 'light';
            this.setTheme(systemTheme);
        };

        mediaQuery.addListener(handleChange);
        
        // Set initial theme based on system preference
        const systemTheme = this.detectSystemTheme();
        this.setTheme(systemTheme);
    }
}

// Initialize theme manager when DOM is loaded
let themeManager;

document.addEventListener('DOMContentLoaded', () => {
    themeManager = new ThemeManager();
});

// Export for global access
window.ThemeManager = ThemeManager;