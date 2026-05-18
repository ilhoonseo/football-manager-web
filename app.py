import os
import random

from flask import Flask, jsonify, render_template, request

from config import config
from game_engine import League, MatchSimulator, TACTICS
from player import Player, Position
from team import Team


FORMATIONS = {"4-3-3", "4-2-4", "3-5-2", "5-3-2"}
DEFAULT_TEAM_NAMES = ["이비지니스", "디지털컨텐츠", "웹프로래밍", "해킹방어"]
STARTING_POSITIONS = [Position.GK, *([Position.DEF] * 4), *([Position.MID] * 3), *([Position.FWD] * 3)]

TEAM_ROSTERS = {
    "이비지니스": [
        ("강승진", 82),
        ("국민우", 80),
        ("권은진", 81),
        ("금명구", 79),
        ("김동현", 83),
        ("김민성", 78),
        ("김보균", 80),
        ("김성근", 82),
        ("김수환", 81),
        ("김재환", 79),
        ("김지수", 84),
    ],
    "디지털컨텐츠": [
        ("김호영", 80),
        ("남궁곤", 82),
        ("남준우", 79),
        ("문원주", 81),
        ("민성경", 83),
        ("박경열", 78),
        ("박대현", 80),
        ("박병주", 79),
        ("박상수", 82),
        ("박정현", 81),
        ("박치완", 80),
    ],
    "웹프로래밍": [
        ("서일훈", 85),
        ("신형록", 81),
        ("유진혁", 80),
        ("이인혜", 83),
        ("임준석", 79),
        ("전영우", 82),
        ("정락준", 80),
        ("정우영", 81),
        ("최서현", 83),
        ("허재원", 79),
        ("허정민", 80),
    ],
    "해킹방어": [
        ("홍정웅", 82),
        ("홍형순", 81),
        ("양덕모", 80),
        ("박정진", 83),
        ("펠레", 96),
        ("마라도나", 95),
        ("메시", 97),
        ("호날두", 96),
        ("지단", 94),
        ("호나우지뉴", 93),
        ("베켄바워", 94),
    ],
}


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name or os.environ.get("FLASK_ENV", "default")])
    app.games = {}
    register_routes(app)
    return app


def register_routes(app: Flask) -> None:
    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/game/start")
    def start_game():
        game_id = os.urandom(16).hex()
        teams = [create_team(team_name) for team_name in DEFAULT_TEAM_NAMES]
        player_team = teams[0]
        cpu_teams = teams[1:]
        league = League(teams)
        app.games[game_id] = {
            "player_team": player_team,
            "cpu_teams": cpu_teams,
            "league": league,
            "match_results": [],
        }
        return jsonify(game_payload(game_id, app.games[game_id]))

    @app.get("/api/game/<game_id>/status")
    def game_status(game_id):
        game = app.games.get(game_id)
        if not game:
            return game_not_found()
        return jsonify(game_payload(game_id, game))

    @app.post("/api/game/<game_id>/formation")
    def update_formation(game_id):
        game = app.games.get(game_id)
        if not game:
            return game_not_found()

        data = request.get_json(silent=True) or {}
        formation = data.get("formation")
        tactics = data.get("tactics")
        player_team = game["player_team"]

        if formation not in FORMATIONS:
            return jsonify({"success": False, "error": "지원하지 않는 포메이션입니다."}), 400
        if tactics not in TACTICS:
            return jsonify({"success": False, "error": "지원하지 않는 전술입니다."}), 400

        player_team.formation = formation
        player_team.tactics = tactics
        return jsonify(game_payload(game_id, game))

    @app.post("/api/game/<game_id>/match")
    def play_match(game_id):
        game = app.games.get(game_id)
        if not game:
            return game_not_found()

        player_team = game["player_team"]
        opponent = random.choice(game["cpu_teams"])
        home_goals, away_goals = MatchSimulator.simulate_match(player_team, opponent)
        result = MatchSimulator.update_standings(player_team, opponent, home_goals, away_goals)
        match_info = game["league"].record_match(player_team, opponent, home_goals, away_goals, result)
        game["match_results"].insert(0, match_info)

        return jsonify({**game_payload(game_id, game), "match": match_info})

    @app.post("/api/game/<game_id>/reset")
    def reset_game(game_id):
        game = app.games.get(game_id)
        if not game:
            return game_not_found()
        for team in game["league"].teams:
            team.reset_record()
        game["league"].match_history.clear()
        game["league"].current_week = 1
        game["match_results"].clear()
        return jsonify(game_payload(game_id, game))


def game_payload(game_id: str, game: dict) -> dict:
    return {
        "success": True,
        "game_id": game_id,
        "player_team": game["player_team"].to_dict(),
        "standings": game["league"].get_standings_dict(),
        "match_results": game["match_results"][:6],
        "tactics": TACTICS,
        "formations": sorted(FORMATIONS),
    }


def game_not_found():
    return jsonify({"success": False, "error": "게임을 찾을 수 없습니다. 새 게임을 시작해 주세요."}), 404


def create_team(name: str) -> Team:
    team = Team(name)
    for position, (player_name, overall) in zip(STARTING_POSITIONS, TEAM_ROSTERS[name]):
        team.add_player(Player(player_name, position, overall))

    return team


app = create_app("production")


if __name__ == "__main__":
    development_app = create_app("development")
    development_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
