let score = [0, 0];
let currentServer = 1;
let gameOver = false;

function startGame() {
    const player1Name = document.getElementById('player1').value;
    const player2Name = document.getElementById('player2').value;

    document.getElementById('name1').innerText = player1Name;
    document.getElementById('name2').innerText = player2Name;
    document.getElementById('game').style.display = 'block';
    document.getElementById('setup').style.display = 'none';

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
        const name1 = document.getElementById('name1').innerText;
        const name2 = document.getElementById('name2').innerText;
        const winner = score[0] > score[1] ? name1 : name2;

        document.getElementById('winner').innerText = `Победитель: ${winner}`;
        gameOver = true;

        // 📨 Сохраняем на сервер
        fetch("/api/save_friendly_game/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                player1: name1,
                player2: name2,
                winner: winner,
                score1: score[0],
                score2: score[1]
            })
        }).then(res => {
            if (!res.ok) console.error("Ошибка сохранения игры");
        });
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
    document.getElementById('game').style.display = 'none';
    document.getElementById('setup').style.display = 'block';
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