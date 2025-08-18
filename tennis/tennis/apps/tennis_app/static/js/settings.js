// JavaScript для страницы настроек
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация настроек
    initializeSettings();
    
    // Обработчики событий
    setupThemeControls();
    setupPerformanceControls();
    setupDeveloperTools();
    updateSystemInfo();
});

function initializeSettings() {
    // Установка текущей темы
    const currentTheme = UI.getPreferredTheme();
    document.querySelectorAll('.theme-option').forEach(option => {
        option.classList.remove('active');
        if (option.dataset.theme === currentTheme) {
            option.classList.add('active');
        }
    });
    
    // Установка текущего режима производительности
    const currentPerformance = UI.getPerformanceMode();
    document.querySelectorAll('.performance-option').forEach(option => {
        option.classList.remove('active');
        if (option.dataset.mode === currentPerformance) {
            option.classList.add('active');
        }
    });
    
    // Состояние FPS монитора
    const fpsToggle = document.getElementById('fps-monitor-toggle');
    if (fpsToggle) {
        fpsToggle.checked = PerformanceMonitor.isRunning();
    }
}

function setupThemeControls() {
    document.querySelectorAll('.theme-option').forEach(option => {
        option.addEventListener('click', function() {
            const theme = this.dataset.theme;
            
            // Обновляем активный элемент
            document.querySelectorAll('.theme-option').forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            // Применяем тему
            if (theme === 'auto') {
                // Автоматическая тема
                localStorage.removeItem('theme');
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                UI.setTheme(prefersDark ? 'dark' : 'light');
            } else {
                UI.setTheme(theme);
            }
            
            showFeedback(`Тема изменена на: ${getThemeName(theme)}`);
        });
    });
}

function setupPerformanceControls() {
    document.querySelectorAll('.performance-option').forEach(option => {
        option.addEventListener('click', function() {
            const mode = this.dataset.mode;
            
            // Обновляем активный элемент
            document.querySelectorAll('.performance-option').forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            // Применяем режим
            UI.setPerformanceMode(mode);
            
            showFeedback(`Режим производительности: ${getPerformanceModeName(mode)}`);
        });
    });
}

function setupDeveloperTools() {
    // FPS монитор
    const fpsToggle = document.getElementById('fps-monitor-toggle');
    if (fpsToggle) {
        fpsToggle.addEventListener('change', function() {
            if (this.checked) {
                PerformanceMonitor.start();
                showFeedback('FPS монитор включен');
            } else {
                PerformanceMonitor.stop();
                showFeedback('FPS монитор выключен');
            }
        });
    }
    
    // Бенчмарк
    const benchmarkBtn = document.getElementById('run-benchmark');
    if (benchmarkBtn) {
        benchmarkBtn.addEventListener('click', function() {
            showFeedback('Запуск теста производительности...');
            
            setTimeout(() => {
                const results = PerformanceMonitor.benchmark();
                showDetailedBenchmarkResults(results);
            }, 500);
        });
    }
    
    // Сброс настроек
    const resetBtn = document.getElementById('reset-settings');
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            if (confirm('Сбросить все настройки к значениям по умолчанию?')) {
                resetAllSettings();
            }
        });
    }
}

function updateSystemInfo() {
    // Информация о браузере
    const browserInfo = getBrowserInfo();
    document.getElementById('browser-info').textContent = browserInfo;
    
    // Ядра процессора
    const cores = navigator.hardwareConcurrency || 'Неизвестно';
    document.getElementById('cpu-cores').textContent = cores;
    
    // Память
    const memory = navigator.deviceMemory ? `${navigator.deviceMemory} GB` : 'Неизвестно';
    document.getElementById('device-memory').textContent = memory;
    
    // Тип сети
    const networkType = navigator.connection ? navigator.connection.effectiveType : 'Неизвестно';
    document.getElementById('network-type').textContent = networkType;
    
    // Уменьшенная анимация
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'Включена' : 'Выключена';
    document.getElementById('reduced-motion').textContent = reducedMotion;
}

function getBrowserInfo() {
    const userAgent = navigator.userAgent;
    
    if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) {
        return 'Chrome';
    } else if (userAgent.includes('Firefox')) {
        return 'Firefox';
    } else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
        return 'Safari';
    } else if (userAgent.includes('Edg')) {
        return 'Edge';
    } else {
        return 'Другой';
    }
}

function getThemeName(theme) {
    const names = {
        'light': 'Светлая',
        'dark': 'Тёмная',
        'auto': 'Автоматическая'
    };
    return names[theme] || theme;
}

function getPerformanceModeName(mode) {
    const names = {
        'performance': 'Производительность',
        'balanced': 'Сбалансированный',
        'visual': 'Визуальный'
    };
    return names[mode] || mode;
}

function showFeedback(message, type = 'success') {
    const feedback = document.createElement('div');
    feedback.className = `settings-feedback ${type}`;
    feedback.textContent = message;
    
    feedback.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success-gradient);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: var(--shadow-xl);
        z-index: 10001;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        max-width: 300px;
    `;
    
    if (type === 'error') {
        feedback.style.background = 'var(--danger-gradient)';
    } else if (type === 'info') {
        feedback.style.background = 'var(--secondary-gradient)';
    }
    
    document.body.appendChild(feedback);
    
    // Анимация появления
    requestAnimationFrame(() => {
        feedback.style.opacity = '1';
        feedback.style.transform = 'translateX(0)';
    });
    
    // Удаление через 3 секунды
    setTimeout(() => {
        feedback.style.opacity = '0';
        feedback.style.transform = 'translateX(100%)';
        setTimeout(() => feedback.remove(), 300);
    }, 3000);
}

function showDetailedBenchmarkResults(results) {
    const modal = document.createElement('div');
    modal.className = 'benchmark-modal';
    modal.innerHTML = `
        <div class="benchmark-content">
            <h3>🧪 Результаты теста производительности</h3>
            
            <div class="benchmark-section">
                <h4>📱 Характеристики устройства</h4>
                <div class="benchmark-grid">
                    <div class="benchmark-item">
                        <strong>Ядра процессора:</strong>
                        <span>${results.device.cores}</span>
                    </div>
                    <div class="benchmark-item">
                        <strong>Объем памяти:</strong>
                        <span>${results.device.memory}</span>
                    </div>
                    <div class="benchmark-item">
                        <strong>Тип соединения:</strong>
                        <span>${results.device.connection}</span>
                    </div>
                    <div class="benchmark-item">
                        <strong>Уменьшенная анимация:</strong>
                        <span>${results.device.reducedMotion ? 'Включена' : 'Выключена'}</span>
                    </div>
                </div>
            </div>
            
            <div class="benchmark-section">
                <h4>⚡ Производительность</h4>
                <div class="benchmark-grid">
                    <div class="benchmark-item">
                        <strong>Текущий режим:</strong>
                        <span>${getPerformanceModeName(results.performance.currentMode)}</span>
                    </div>
                    <div class="benchmark-item">
                        <strong>FPS:</strong>
                        <span>${results.performance.currentFPS}</span>
                    </div>
                </div>
            </div>
            
            <div class="benchmark-recommendations">
                <h4>💡 Рекомендации</h4>
                <div id="benchmark-recommendations-content"></div>
            </div>
            
            <button class="btn primary benchmark-close">Закрыть</button>
        </div>
    `;
    
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10002;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    const content = modal.querySelector('.benchmark-content');
    content.style.cssText = `
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--radius-xl);
        padding: 2rem;
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
        color: var(--text-primary);
        transform: scale(0.9);
        transition: transform 0.3s ease;
    `;
    
    // Добавляем рекомендации
    const recommendationsContent = modal.querySelector('#benchmark-recommendations-content');
    const recommendations = generateRecommendations(results);
    recommendationsContent.innerHTML = recommendations;
    
    document.body.appendChild(modal);
    
    // Анимация появления
    requestAnimationFrame(() => {
        modal.style.opacity = '1';
        content.style.transform = 'scale(1)';
    });
    
    // Закрытие
    modal.querySelector('.benchmark-close').addEventListener('click', () => {
        modal.style.opacity = '0';
        content.style.transform = 'scale(0.9)';
        setTimeout(() => modal.remove(), 300);
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.querySelector('.benchmark-close').click();
        }
    });
}

function generateRecommendations(results) {
    const recommendations = [];
    
    // Анализ ядер процессора
    if (results.device.cores < 4) {
        recommendations.push('⚡ Рекомендуется режим "Производительность" из-за малого количества ядер процессора');
    } else if (results.device.cores >= 8) {
        recommendations.push('✨ Можно использовать режим "Визуальный" - у вас мощный процессор');
    }
    
    // Анализ памяти
    if (results.device.memory && results.device.memory.includes('GB')) {
        const memoryAmount = parseFloat(results.device.memory);
        if (memoryAmount < 4) {
            recommendations.push('⚡ Рекомендуется режим "Производительность" из-за малого объема памяти');
        } else if (memoryAmount >= 8) {
            recommendations.push('✨ Достаточно памяти для режима "Визуальный"');
        }
    }
    
    // Анализ FPS
    if (results.performance.currentFPS < 30) {
        recommendations.push('⚠️ Низкий FPS - переключитесь на режим "Производительность"');
    } else if (results.performance.currentFPS >= 55) {
        recommendations.push('✅ Отличная производительность - можно использовать любой режим');
    }
    
    // Анализ уменьшенной анимации
    if (results.device.reducedMotion) {
        recommendations.push('♿ Включена настройка "Уменьшенная анимация" - автоматически используется режим "Производительность"');
    }
    
    // Анализ соединения
    if (results.device.connection === 'slow-2g' || results.device.connection === '2g') {
        recommendations.push('📶 Медленное соединение - рекомендуется режим "Производительность" для быстрой загрузки');
    }
    
    if (recommendations.length === 0) {
        recommendations.push('✅ Все характеристики в норме - можете использовать любой режим производительности');
    }
    
    return recommendations.map(rec => `<div class="recommendation-item">${rec}</div>`).join('');
}

function resetAllSettings() {
    // Сброс темы
    localStorage.removeItem('theme');
    UI.setTheme('light');
    
    // Сброс режима производительности
    localStorage.removeItem('performanceMode');
    UI.setPerformanceMode('balanced');
    
    // Выключение FPS монитора
    PerformanceMonitor.stop();
    
    // Обновление интерфейса
    initializeSettings();
    
    showFeedback('Все настройки сброшены к значениям по умолчанию');
}

// Дополнительные стили для модального окна
const benchmarkStyles = document.createElement('style');
benchmarkStyles.textContent = `
    .benchmark-section {
        margin-bottom: 2rem;
    }
    
    .benchmark-section h4 {
        margin-bottom: 1rem;
        color: var(--text-primary);
        font-size: 1.1rem;
    }
    
    .benchmark-grid {
        display: grid;
        gap: 0.75rem;
    }
    
    .benchmark-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-md);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .benchmark-item strong {
        color: var(--text-primary);
    }
    
    .benchmark-item span {
        color: var(--text-secondary);
        font-family: monospace;
    }
    
    .benchmark-recommendations {
        background: rgba(102, 126, 234, 0.05);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .recommendation-item {
        padding: 0.5rem 0;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    .benchmark-close {
        width: 100%;
        margin-top: 1rem;
    }
`;
document.head.appendChild(benchmarkStyles);
