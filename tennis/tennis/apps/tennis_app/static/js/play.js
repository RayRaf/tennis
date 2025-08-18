let score = [0, 0];
let currentServer = 1;
let gameOver = false;

function startGame() {
    const player1Name = document.getElementById('player1').value;
    const player2Name = document.getElementById('player2').value;

    if (!player1Name.trim() || !player2Name.trim()) {
        alert('Пожалуйста, введите имена игроков');
        return;
    }

    document.getElementById('name1').innerText = player1Name;
    document.getElementById('name2').innerText = player2Name;
    
    // Добавляем анимации
    const setupDiv = document.getElementById('setup');
    const gameDiv = document.getElementById('game');
    
    setupDiv.classList.add('fade-out');
    
    setTimeout(() => {
        setupDiv.style.display = 'none';
        gameDiv.style.display = 'block';
        gameDiv.classList.add('fade-in');
    }, 400);

    document.getElementById('btnAdd1').innerText = `+1 ${player1Name}`;
    document.getElementById('btnAdd2').innerText = `+1 ${player2Name}`;
    document.getElementById('btnRemove1').innerText = `-1 ${player1Name}`;
    document.getElementById('btnRemove2').innerText = `-1 ${player2Name}`;

    updateTurn();
}

function addPoint(player) {
    if (gameOver) return;
    score[player - 1]++;
    document.getElementById(`score${player}`).innerText = score[player - 1];
    checkWinner();
    updateTurn();
}

function removePoint(player) {
    if (score[player - 1] > 0) {
        score[player - 1]--;
        document.getElementById(`score${player}`).innerText = score[player - 1];
        checkWinner();
        updateTurn();
    }
}

function checkWinner() {
    const diff = Math.abs(score[0] - score[1]);
    const maxScore = Math.max(score[0], score[1]);

    if (maxScore >= 11 && diff >= 2) {
        const winnerName = score[0] > score[1] ? document.getElementById('name1').innerText : document.getElementById('name2').innerText;
        document.getElementById('winner').innerText = `Победитель: ${winnerName}`;
        gameOver = true;
    } else {
        document.getElementById('winner').innerText = '';
        gameOver = false;
    }

    document.getElementById('btnAdd1').disabled = gameOver;
    document.getElementById('btnAdd2').disabled = gameOver;
}

function updateTurn() {
    let totalPoints = score[0] + score[1];
    
    // Логика подач в настольном теннисе
    if (score[0] >= 10 && score[1] >= 10) {
        // Дейс: по 1 подаче, чередуем каждое очко
        currentServer = (totalPoints % 2 === 0) ? 1 : 2;
    } else {
        // Обычная игра: по 2 подачи каждого игрока
        const serveGroup = Math.floor(totalPoints / 2);
        currentServer = (serveGroup % 2 === 0) ? 1 : 2;
    }
    
    let turnText = `Подает: ${document.getElementById(`name${currentServer}`).innerText}`;
    
    // Добавляем индикатор дейса
    if (score[0] >= 10 && score[1] >= 10) {
        turnText += ' (ДЕЙС)';
    }
    
    document.getElementById('turn').innerText = turnText;
    document.getElementById('p1').classList.toggle('active', currentServer === 1);
    document.getElementById('p2').classList.toggle('active', currentServer === 2);
}

function resetGame() {
    score = [0, 0];
    document.getElementById('score1').innerText = '0';
    document.getElementById('score2').innerText = '0';
    document.getElementById('turn').innerText = '';
    document.getElementById('winner').innerText = '';
    
    // Добавляем анимации
    const setupDiv = document.getElementById('setup');
    const gameDiv = document.getElementById('game');
    
    gameDiv.classList.add('fade-out');
    
    setTimeout(() => {
        gameDiv.style.display = 'none';
        gameDiv.classList.remove('fade-out', 'fade-in');
        setupDiv.style.display = 'block';
        setupDiv.classList.remove('fade-out');
    }, 400);
    
    gameOver = false;
    document.getElementById('btnAdd1').disabled = false;
    document.getElementById('btnAdd2').disabled = false;
}