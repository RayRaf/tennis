window.UI = (function() {
    // Performance settings
    let performanceMode = localStorage.getItem('performanceMode') || 'balanced'; // 'performance', 'balanced', 'visual'
    
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
        
        // Добавляем анимацию переключения только в режиме visual
        if (toggleButton && performanceMode === 'visual') {
            toggleButton.classList.add('switching');
            setTimeout(() => {
                toggleButton.classList.remove('switching');
            }, 600);
        }
        
        setTheme(newTheme);
        
        // Add smooth transition effect only in visual mode
        if (performanceMode === 'visual') {
            document.body.style.transition = 'background 0.5s ease, color 0.5s ease';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 500);
        }
    };

    // Performance management
    const setPerformanceMode = (mode) => {
        performanceMode = mode;
        localStorage.setItem('performanceMode', mode);
        applyPerformanceSettings();
    };

    const applyPerformanceSettings = () => {
        const body = document.body;
        const performanceClass = `performance-${performanceMode}`;
        
        // Remove existing performance classes
        body.classList.remove('performance-performance', 'performance-balanced', 'performance-visual');
        body.classList.add(performanceClass);
        
        switch(performanceMode) {
            case 'performance':
                // Максимальная производительность - отключаем все анимации
                addPerformanceCSS();
                break;
            case 'balanced':
                // Сбалансированный режим - оставляем только важные анимации
                addBalancedCSS();
                break;
            case 'visual':
                // Полная визуальная красота - включаем все анимации
                addVisualCSS();
                break;
        }
    };

    const addPerformanceCSS = () => {
        let style = document.getElementById('performance-mode-styles');
        if (!style) {
            style = document.createElement('style');
            style.id = 'performance-mode-styles';
            document.head.appendChild(style);
        }
        
        style.textContent = `
            .performance-performance *,
            .performance-performance *::before,
            .performance-performance *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
            
            .performance-performance body::before,
            .performance-performance body::after {
                display: none !important;
            }
            
            .performance-performance {
                background: linear-gradient(-45deg, var(--bg-gradient-1), var(--bg-gradient-3)) !important;
            }
        `;
    };

    const addBalancedCSS = () => {
        let style = document.getElementById('performance-mode-styles');
        if (!style) {
            style = document.createElement('style');
            style.id = 'performance-mode-styles';
            document.head.appendChild(style);
        }
        
        style.textContent = `
            .performance-balanced body {
                background-size: 300% 300% !important;
                animation: gradientShift 30s ease infinite !important;
            }
            
            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            .performance-balanced body::before,
            .performance-balanced body::after {
                opacity: 0.4;
                animation: floatingOrbs 45s ease-in-out infinite !important;
                filter: blur(8px) !important;
            }
            
            .performance-balanced body::after {
                animation: floatingOrbs 50s ease-in-out infinite reverse !important;
            }
            
            @keyframes floatingOrbs {
                0%, 100% { 
                    transform: translateY(0px) translateX(0px) scale(1);
                    opacity: 0.4;
                }
                50% { 
                    transform: translateY(-10px) translateX(10px) scale(1.03);
                    opacity: 0.6;
                }
            }
            
            .performance-balanced .activePlayerGlow,
            .performance-balanced .scoreGlow,
            .performance-balanced .winnerAnimation {
                animation-duration: 1s !important;
            }
        `;
    };

    const addVisualCSS = () => {
        let style = document.getElementById('performance-mode-styles');
        if (!style) {
            style = document.createElement('style');
            style.id = 'performance-mode-styles';
            document.head.appendChild(style);
        }
        
        style.textContent = `
            .performance-visual body {
                background-size: 400% 400% !important;
                animation: gradientShift 15s ease infinite !important;
            }
            
            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            .performance-visual body::before {
                animation: floatingOrbs 20s ease-in-out infinite !important;
                filter: blur(15px) !important;
            }
            
            .performance-visual body::after {
                animation: floatingOrbs 25s ease-in-out infinite reverse !important;
                filter: blur(20px) !important;
            }
            
            @keyframes floatingOrbs {
                0%, 100% { 
                    transform: translateY(0px) translateX(0px) scale(1) rotate(0deg);
                    opacity: 0.6;
                }
                25% { 
                    transform: translateY(-20px) translateX(-15px) scale(1.08) rotate(1.5deg);
                    opacity: 0.8;
                }
                50% { 
                    transform: translateY(-8px) translateX(20px) scale(0.92) rotate(-0.8deg);
                    opacity: 0.7;
                }
                75% { 
                    transform: translateY(15px) translateX(-8px) scale(1.04) rotate(0.8deg);
                    opacity: 0.9;
                }
            }
        `;
    };

    // Auto-detect performance needs
    const detectPerformanceNeeds = () => {
        if (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4) {
            return 'performance';
        }
        
        if (navigator.deviceMemory && navigator.deviceMemory < 4) {
            return 'performance';
        }
        
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return 'performance';
        }
        
        return 'balanced';
    };

    // Menu management
    const toggleMenu = () => {
        const nav = document.getElementById('navLinks');
        const toggle = document.querySelector('.nav-toggle');
        const overlay = document.getElementById('navOverlay');
        
        if (nav) {
            const isOpen = nav.classList.contains('show');
            
            if (isOpen) {
                // Закрываем меню
                nav.classList.remove('show');
                if (toggle) toggle.classList.remove('active');
                if (overlay) overlay.classList.remove('show');
                document.body.style.overflow = '';
            } else {
                // Открываем меню
                nav.classList.add('show');
                if (toggle) toggle.classList.add('active');
                if (overlay) overlay.classList.add('show');
                document.body.style.overflow = 'hidden'; // Предотвращаем скролл
            }
        }
    };

    // Initialize theme and performance on load
    const initTheme = () => {
        setTheme(getPreferredTheme());
        
        // Auto-detect if no performance mode is set
        if (!localStorage.getItem('performanceMode')) {
            setPerformanceMode(detectPerformanceNeeds());
        } else {
            applyPerformanceSettings();
        }
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
        
        // Listen for reduced motion preference changes
        window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
            if (e.matches && performanceMode !== 'performance') {
                setPerformanceMode('performance');
            }
        });
    };

    // Create performance toggle UI
    const createPerformanceToggle = () => {
        const toggle = document.createElement('div');
        toggle.className = 'performance-toggle';
        toggle.innerHTML = `
            <div class="performance-indicator">Режим производительности</div>
            <button class="performance-btn ${performanceMode === 'performance' ? 'active' : ''}" data-mode="performance" title="Производительность">⚡</button>
            <button class="performance-btn ${performanceMode === 'balanced' ? 'active' : ''}" data-mode="balanced" title="Сбалансированный">⚖️</button>
            <button class="performance-btn ${performanceMode === 'visual' ? 'active' : ''}" data-mode="visual" title="Визуальный">✨</button>
        `;
        
        toggle.addEventListener('click', (e) => {
            if (e.target.classList.contains('performance-btn')) {
                const mode = e.target.dataset.mode;
                setPerformanceMode(mode);
                
                // Update active state
                toggle.querySelectorAll('.performance-btn').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
                
                // Show feedback
                showPerformanceFeedback(mode);
            }
        });
        
        return toggle;
    };

    // Show performance mode change feedback
    const showPerformanceFeedback = (mode) => {
        const modeNames = {
            'performance': 'Режим производительности',
            'balanced': 'Сбалансированный режим', 
            'visual': 'Визуальный режим'
        };
        
        const feedback = document.createElement('div');
        feedback.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--success-gradient);
            color: white;
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            box-shadow: var(--shadow-lg);
            z-index: 10001;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        feedback.textContent = `Включен: ${modeNames[mode]}`;
        
        document.body.appendChild(feedback);
        
        // Animate in
        setTimeout(() => feedback.style.opacity = '1', 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            feedback.style.opacity = '0';
            setTimeout(() => feedback.remove(), 300);
        }, 3000);
    };

    // Navbar scroll effect
    const handleScroll = () => {
        const header = document.querySelector('.site-header');
        if (header) {
            if (window.scrollY > 20) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }
    };

    // Initialize scroll listener
    const initScrollEffects = () => {
        if (performanceMode !== 'performance') {
            window.addEventListener('scroll', handleScroll, { passive: true });
        }
    };

    // Escape key handler for mobile menu
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            const nav = document.getElementById('navLinks');
            if (nav && nav.classList.contains('show')) {
                toggleMenu();
            }
        }
    };

    // Highlight active menu item
    const highlightActiveMenuItem = () => {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-links a');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            const linkPath = new URL(link.href).pathname;
            
            if (currentPath === linkPath || 
                (currentPath.startsWith(linkPath) && linkPath !== '/')) {
                link.classList.add('active');
            }
        });
    };

    // Auto-initialize when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initTheme();
            initScrollEffects();
            highlightActiveMenuItem();
            document.addEventListener('keydown', handleEscape);
            // Performance toggle moved to settings page
        });
    } else {
        initTheme();
        initScrollEffects();
        highlightActiveMenuItem();
        document.addEventListener('keydown', handleEscape);
        // Performance toggle moved to settings page
    }

    return {
        toggleMenu,
        toggleTheme,
        setTheme,
        getPreferredTheme,
        setPerformanceMode,
        getPerformanceMode: () => performanceMode
    };
})();
