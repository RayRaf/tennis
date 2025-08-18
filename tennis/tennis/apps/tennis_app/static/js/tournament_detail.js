/**
 * JavaScript функции для страницы детализации турнира
 * Включает функционал матрицы результатов и сворачивания списка матчей
 */

// Глобальные переменные
let playersData = {};

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    initializeTournamentDetail();
});

/**
 * Инициализация всех функций страницы
 */
function initializeTournamentDetail() {
    initializeMatchesToggle();
    initializeModalHandlers();
    loadPlayersData();
}

/**
 * Загрузка данных об игроках
 */
function loadPlayersData() {
    // Данные игроков должны быть переданы из шаблона
    const playersScript = document.getElementById('players-data');
    if (playersScript) {
        try {
            playersData = JSON.parse(playersScript.textContent);
        } catch (e) {
            console.error('Ошибка загрузки данных игроков:', e);
        }
    }
}

/**
 * Инициализация функционала сворачивания списка матчей
 */
function initializeMatchesToggle() {
    const matchesList = document.getElementById('matchesList');
    const toggleBtn = document.getElementById('toggleMatchesBtn');
    
    if (!matchesList || !toggleBtn) return;
    
    // Восстанавливаем состояние из localStorage
    const isExpanded = localStorage.getItem('matchesExpanded') === 'true';
    
    if (isExpanded) {
        showMatches();
    } else {
        hideMatches();
    }
}

/**
 * Переключение видимости списка матчей
 */
function toggleMatches() {
    const matchesList = document.getElementById('matchesList');
    const isVisible = matchesList.style.display !== 'none';
    
    if (isVisible) {
        hideMatches();
    } else {
        showMatches();
    }
}

/**
 * Показать список матчей
 */
function showMatches() {
    const matchesList = document.getElementById('matchesList');
    const toggleBtn = document.getElementById('toggleMatchesBtn');
    const toggleText = toggleBtn?.querySelector('.toggle-text');
    
    if (matchesList) {
        matchesList.style.display = 'block';
        setTimeout(() => {
            matchesList.classList.add('show');
        }, 10);
    }
    
    if (toggleBtn) {
        toggleBtn.classList.add('expanded');
    }
    
    if (toggleText) {
        toggleText.textContent = 'Свернуть список матчей';
    }
    
    localStorage.setItem('matchesExpanded', 'true');
}

/**
 * Скрыть список матчей
 */
function hideMatches() {
    const matchesList = document.getElementById('matchesList');
    const toggleBtn = document.getElementById('toggleMatchesBtn');
    const toggleText = toggleBtn?.querySelector('.toggle-text');
    
    if (matchesList) {
        matchesList.classList.remove('show');
        setTimeout(() => {
            matchesList.style.display = 'none';
        }, 300);
    }
    
    if (toggleBtn) {
        toggleBtn.classList.remove('expanded');
    }
    
    if (toggleText) {
        toggleText.textContent = 'Развернуть список матчей';
    }
    
    localStorage.setItem('matchesExpanded', 'false');
}

/**
 * Инициализация обработчиков модального окна
 */
function initializeModalHandlers() {
    // Закрытие модального окна при клике вне его
    window.onclick = function(event) {
        const modal = document.getElementById('matchModal');
        if (event.target === modal) {
            closeMatchModal();
        }
    };
    
    // Закрытие модального окна по Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeMatchModal();
        }
    });
}

/**
 * Открытие модального окна для создания матча
 * @param {HTMLElement} cell - Ячейка матрицы результатов
 */
function openMatchModal(cell) {
    const player1Id = cell.getAttribute('data-player1');
    const player2Id = cell.getAttribute('data-player2');
    
    if (player1Id === player2Id) {
        return; // Не позволяем создавать матч игрока с самим собой
    }
    
    const player1Name = playersData[player1Id] || 'Неизвестный игрок';
    const player2Name = playersData[player2Id] || 'Неизвестный игрок';
    
    // Заполняем данные в модальном окне
    const matchPlayersElement = document.getElementById('matchPlayers');
    const modalPlayer1Element = document.getElementById('modalPlayer1');
    const modalPlayer2Element = document.getElementById('modalPlayer2');
    const modal = document.getElementById('matchModal');
    
    if (matchPlayersElement) {
        matchPlayersElement.textContent = `${player1Name} vs ${player2Name}`;
    }
    
    if (modalPlayer1Element) {
        modalPlayer1Element.value = player1Id;
    }
    
    if (modalPlayer2Element) {
        modalPlayer2Element.value = player2Id;
    }
    
    // Показываем модальное окно
    if (modal) {
        modal.style.display = 'block';
        
        // Добавляем анимацию появления
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    }
}

/**
 * Начало матча при клике на ячейку с матчем в процессе
 * @param {HTMLElement} cell - Ячейка матрицы результатов
 */
function startMatch(cell) {
    const matchId = cell.getAttribute('data-match-id');
    
    if (!matchId) {
        showNotification('Ошибка: ID матча не найден', 'error');
        return;
    }
    
    // Показываем уведомление о переходе
    showNotification('Переход к матчу...', 'info');
    
    // Переходим на страницу живого матча
    window.location.href = `/match/${matchId}/play/`;
}

/**
 * Закрытие модального окна
 */
function closeMatchModal() {
    const modal = document.getElementById('matchModal');
    
    if (modal) {
        modal.classList.remove('show');
        
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

/**
 * Обработка отправки формы создания матча
 */
function handleCreateMatchForm() {
    const form = document.getElementById('createMatchForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            const player1Id = document.getElementById('modalPlayer1').value;
            const player2Id = document.getElementById('modalPlayer2').value;
            
            if (!player1Id || !player2Id || player1Id === player2Id) {
                e.preventDefault();
                alert('Пожалуйста, выберите двух разных игроков');
                return false;
            }
            
            // Показываем индикатор загрузки
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Создание...';
            }
        });
    }
}

/**
 * Анимация ячеек матрицы при наведении
 */
function initializeMatrixAnimations() {
    const emptyCells = document.querySelectorAll('.matrix-cell.cell-empty');
    const progressCells = document.querySelectorAll('.matrix-cell.cell-progress');
    
    // Анимации для пустых ячеек
    emptyCells.forEach(cell => {
        cell.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.borderColor = 'rgba(102, 126, 234, 0.8)';
        });
        
        cell.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.borderColor = 'rgba(102, 126, 234, 0.3)';
        });
    });
    
    // Анимации для ячеек с матчами в процессе
    progressCells.forEach(cell => {
        cell.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1) rotate(2deg)';
            this.style.boxShadow = '0 8px 25px rgba(67, 233, 123, 0.5)';
        });
        
        cell.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
            this.style.boxShadow = 'var(--shadow-md)';
        });
    });
}

/**
 * Утилита для показа уведомлений
 * @param {string} message - Текст сообщения
 * @param {string} type - Тип сообщения (success, error, info)
 */
function showNotification(message, type = 'info') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Добавляем стили
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // Устанавливаем цвет в зависимости от типа
    switch (type) {
        case 'success':
            notification.style.background = 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
            break;
        case 'error':
            notification.style.background = 'linear-gradient(135deg, #ff7f50 0%, #ffa500 100%)';
            break;
        default:
            notification.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
    
    // Добавляем на страницу
    document.body.appendChild(notification);
    
    // Анимация появления
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Автоматическое скрытие через 4 секунды
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Инициализация дополнительных функций при загрузке
document.addEventListener('DOMContentLoaded', function() {
    handleCreateMatchForm();
    initializeMatrixAnimations();
});
