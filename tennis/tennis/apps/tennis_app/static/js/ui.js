window.UI = (function() {
    // Theme management
    const getPreferredTheme = () => {
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme) {
            return storedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    const setTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    };

    const toggleTheme = () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        const toggleButton = document.querySelector('.theme-toggle');
        
        // Добавляем анимацию переключения
        if (toggleButton) {
            toggleButton.classList.add('switching');
            setTimeout(() => {
                toggleButton.classList.remove('switching');
            }, 600);
        }
        
        setTheme(newTheme);
        
        // Add smooth transition effect
        document.body.style.transition = 'background 0.5s ease, color 0.5s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 500);
    };

    // Menu management
    const toggleMenu = () => {
        const nav = document.getElementById('navLinks');
        const toggle = document.querySelector('.nav-toggle');
        if (nav) {
            nav.classList.toggle('show');
            if (toggle) toggle.classList.toggle('active');
        }
    };

    // Initialize theme on load
    const initTheme = () => {
        setTheme(getPreferredTheme());
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
    };

    // Auto-initialize when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }

    return {
        toggleMenu,
        toggleTheme,
        setTheme,
        getPreferredTheme
    };
})();
