const state = {
  gameId: null,
  playerTeam: null,
  standings: [],
  matchResults: [],
};

const formationPositions = {
  "4-3-3": [
    [50, 92], [20, 70], [40, 70], [60, 70], [80, 70],
    [28, 48], [50, 46], [72, 48], [25, 22], [50, 18], [75, 22],
  ],
  "4-2-4": [
    [50, 92], [20, 70], [40, 70], [60, 70], [80, 70],
    [38, 49], [62, 49], [18, 22], [40, 18], [60, 18], [82, 22],
  ],
  "3-5-2": [
    [50, 92], [30, 70], [50, 72], [70, 70],
    [14, 48], [32, 45], [50, 43], [68, 45], [86, 48], [40, 18], [60, 18],
  ],
  "5-3-2": [
    [50, 92], [12, 70], [30, 72], [50, 74], [70, 72], [88, 70],
    [28, 47], [50, 44], [72, 47], [40, 18], [60, 18],
  ],
};

const resultLabels = {
  win: "승리",
  draw: "무승부",
  loss: "패배",
};

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("newGameBtn").addEventListener("click", startGame);
  document.getElementById("matchBtn").addEventListener("click", playMatch);
  document.getElementById("resetBtn").addEventListener("click", resetSeason);
  document.getElementById("saveTacticsBtn").addEventListener("click", saveTactics);
  startGame();
});

async function startGame() {
  const data = await api("/api/game/start", { method: "POST" });
  applyGameState(data);
  setResult("새 시즌이 시작됐습니다. 전술을 고르고 첫 경기를 진행하세요.");
}

async function playMatch() {
  if (!state.gameId) return startGame();
  const data = await api(`/api/game/${state.gameId}/match`, { method: "POST" });
  applyGameState(data);
  const match = data.match;
  setResult(`${match.home_team} ${match.home_goals} : ${match.away_goals} ${match.away_team}<br>${resultLabels[match.result]}`);
}

async function resetSeason() {
  if (!state.gameId) return;
  const data = await api(`/api/game/${state.gameId}/reset`, { method: "POST" });
  applyGameState(data);
  setResult("시즌 기록을 초기화했습니다.");
}

async function saveTactics() {
  if (!state.gameId) return startGame();
  const payload = {
    formation: document.getElementById("formationSelect").value,
    tactics: document.getElementById("tacticsSelect").value,
  };
  const data = await api(`/api/game/${state.gameId}/formation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  applyGameState(data);
  setResult("전술이 저장됐습니다.");
}

async function api(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok || !data.success) {
    throw new Error(data.error || "요청에 실패했습니다.");
  }
  return data;
}

function applyGameState(data) {
  state.gameId = data.game_id;
  state.playerTeam = data.player_team;
  state.standings = data.standings;
  state.matchResults = data.match_results || [];
  renderTeam();
  renderFormation();
  renderStandings();
  renderRecentMatches();
}

function renderTeam() {
  const team = state.playerTeam;
  document.getElementById("teamName").textContent = team.name;
  document.getElementById("record").textContent = `${team.wins}승 ${team.draws}무 ${team.losses}패`;
  document.getElementById("goals").textContent = `${team.goals_for} / ${team.goals_against}`;
  document.getElementById("points").textContent = team.points;
  document.getElementById("strength").textContent = team.team_strength.toFixed(1);
  document.getElementById("formationSelect").value = team.formation;
  document.getElementById("tacticsSelect").value = team.tactics;
}

function renderFormation() {
  const board = document.getElementById("formationBoard");
  const team = state.playerTeam;
  const coords = formationPositions[team.formation] || formationPositions["4-3-3"];
  board.innerHTML = "";
  team.players.forEach((player, index) => {
    const [left, top] = coords[index];
    const node = document.createElement("div");
    node.className = `player ${player.position}`;
    node.style.left = `${left}%`;
    node.style.top = `${top}%`;
    node.title = `${player.name} / ${player.position} / ${player.overall}`;
    node.textContent = `${player.position} ${player.overall}`;
    board.appendChild(node);
  });
}

function renderStandings() {
  const body = document.getElementById("standingsBody");
  body.innerHTML = "";
  state.standings.forEach((row) => {
    const tr = document.createElement("tr");
    if (row.team_name === state.playerTeam.name) tr.classList.add("player-row");
    tr.innerHTML = `
      <td>${row.rank}</td>
      <td>${row.team_name}</td>
      <td>${row.matches}</td>
      <td>${row.wins}</td>
      <td>${row.draws}</td>
      <td>${row.losses}</td>
      <td>${row.goal_diff > 0 ? "+" : ""}${row.goal_diff}</td>
      <td>${row.points}</td>
    `;
    body.appendChild(tr);
  });
}

function renderRecentMatches() {
  const list = document.getElementById("recentMatches");
  list.innerHTML = "";
  state.matchResults.forEach((match) => {
    const item = document.createElement("div");
    item.className = `match-item ${match.result}`;
    item.innerHTML = `
      <strong>${match.week}주차</strong><br>
      ${match.home_team} ${match.home_goals} : ${match.away_goals} ${match.away_team}<br>
      ${resultLabels[match.result]}
    `;
    list.appendChild(item);
  });
}

function setResult(message) {
  document.getElementById("matchResult").innerHTML = message;
}
