const state = {
  gameId: null,
  playerTeam: null,
  standings: [],
  matchResults: [],
  selectedTeam: "이비지니스",
  customPositions: {},
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

let activeDrag = null;

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("newGameBtn").addEventListener("click", startGame);
  document.getElementById("matchBtn").addEventListener("click", playMatch);
  document.getElementById("resetBtn").addEventListener("click", resetSeason);
  document.getElementById("saveTacticsBtn").addEventListener("click", saveTactics);
  document.getElementById("resetLayoutBtn").addEventListener("click", resetLayout);
  document.getElementById("teamSelect").addEventListener("change", startGame);
  document.getElementById("formationSelect").addEventListener("change", renderFormation);
  startGame();
});

async function startGame() {
  const teamSelect = document.getElementById("teamSelect");
  state.selectedTeam = teamSelect.value;
  state.customPositions = {};
  const data = await api("/api/game/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ team_name: state.selectedTeam }),
  });
  applyGameState(data);
  setResult(`${state.playerTeam.name} 소속으로 새 시즌이 시작되었습니다.`);
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
  setResult("전술을 저장했습니다.");
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
  syncTeamOptions(data.team_names || []);
  renderTeam();
  renderFormation();
  renderStandings();
  renderRecentMatches();
}

function syncTeamOptions(teamNames) {
  const teamSelect = document.getElementById("teamSelect");
  if (teamNames.length) {
    teamSelect.innerHTML = teamNames.map((teamName) => `<option>${teamName}</option>`).join("");
  }
  teamSelect.value = state.playerTeam?.name || state.selectedTeam;
  state.selectedTeam = teamSelect.value;
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
  if (!state.playerTeam) return;

  const board = document.getElementById("formationBoard");
  const team = state.playerTeam;
  const formation = document.getElementById("formationSelect").value || team.formation;
  const coords = getPositionsForFormation(formation);
  board.innerHTML = "";
  team.players.forEach((player, index) => {
    const [left, top] = coords[index];
    const node = document.createElement("div");
    node.className = `player ${player.position}`;
    node.dataset.index = String(index);
    node.style.left = `${left}%`;
    node.style.top = `${top}%`;
    node.title = `${player.name} / ${player.position} / ${player.overall}`;
    node.innerHTML = `<span>${player.name}</span><small>${player.position} ${player.overall}</small>`;
    node.addEventListener("pointerdown", startDrag);
    board.appendChild(node);
  });
}

function getPositionsForFormation(formation) {
  const defaults = formationPositions[formation] || formationPositions["4-3-3"];
  const custom = state.customPositions[formation];
  return custom || defaults;
}

function startDrag(event) {
  const playerNode = event.currentTarget;
  activeDrag = {
    node: playerNode,
    pointerId: event.pointerId,
  };
  playerNode.classList.add("dragging");
  playerNode.setPointerCapture(event.pointerId);
  movePlayer(event, playerNode);
  window.addEventListener("pointermove", onDragMove);
  window.addEventListener("pointerup", stopDrag);
  window.addEventListener("pointercancel", stopDrag);
}

function onDragMove(event) {
  if (!activeDrag || activeDrag.pointerId !== event.pointerId) return;
  movePlayer(event, activeDrag.node);
}

function stopDrag(event) {
  if (!activeDrag || activeDrag.pointerId !== event.pointerId) return;
  const playerNode = activeDrag.node;
  playerNode.classList.remove("dragging");
  if (playerNode.hasPointerCapture(event.pointerId)) {
    playerNode.releasePointerCapture(event.pointerId);
  }
  window.removeEventListener("pointermove", onDragMove);
  window.removeEventListener("pointerup", stopDrag);
  window.removeEventListener("pointercancel", stopDrag);
  activeDrag = null;
}

function movePlayer(event, playerNode) {
  const board = document.getElementById("formationBoard");
  const rect = board.getBoundingClientRect();
  const formation = document.getElementById("formationSelect").value;
  const index = Number(playerNode.dataset.index);
  const left = clamp(((event.clientX - rect.left) / rect.width) * 100, 4, 96);
  const top = clamp(((event.clientY - rect.top) / rect.height) * 100, 4, 96);
  const current = getPositionsForFormation(formation).map(([x, y]) => [x, y]);
  current[index] = [left, top];
  state.customPositions[formation] = current;
  playerNode.style.left = `${left}%`;
  playerNode.style.top = `${top}%`;
}

function resetLayout() {
  const formation = document.getElementById("formationSelect").value;
  delete state.customPositions[formation];
  renderFormation();
  setResult(`${formation} 배치를 기본 위치로 되돌렸습니다.`);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
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
