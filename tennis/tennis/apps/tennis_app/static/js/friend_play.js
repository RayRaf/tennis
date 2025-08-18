let score = [0, 0];
let currentServer = 1;
let gameOver = false;

let startTime = null;

function startGame() {
    const player1Name = document.getElementById('player1').value;
    const player2Name = document.getElementById('player2').value;

    if (!player1Name || !player2Name) {
        alert('Пожалуйста, выберите игроков');
        return;
    }

    if (player1Name === player2Name) {
        alert('Выберите разных игроков');
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
    
    document.getElementById('finishGameBtn').style.display = 'inline-block';

    score = [0, 0];
    gameOver = false;
    startTime = new Date().toISOString(); // фиксируем время начала
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
        const winner = score[0] > score[1] ? document.getElementById('name1').innerText : document.getElementById('name2').innerText;
        document.getElementById('winner').innerText = `Победитель: ${winner}`;
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
    currentServer = (score[0] >= 10 && score[1] >= 10) ? totalPoints % 2 + 1 : Math.floor(totalPoints / 2) % 2 + 1;
    document.getElementById('turn').innerText = `Подает: ${document.getElementById(`name${currentServer}`).innerText}`;
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


// Вспомогательная функция для получения CSRF-токена
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name + '=')) {
            return decodeURIComponent(trimmed.substring(name.length + 1));
        }
    }
    return '';
}


function finishGame() {
    if (!gameOver) {
        alert("Сначала завершите игру (один из игроков должен победить).");
        return;
    }

    const data = {
        player1: document.getElementById('name1').innerText,
        player2: document.getElementById('name2').innerText,
        winner: document.getElementById('winner').innerText.replace("Победитель: ", ""),
        score1: score[0],
        score2: score[1],
        start_time: startTime,
        end_time: new Date().toISOString()
    };

    fetch("/api/save_friendly_game/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
        if (res.status === "ok") {
            alert("Игра успешно сохранена!");
            location.reload();
        } else {
            alert("Ошибка при сохранении: " + res.error);
        }
    });
}