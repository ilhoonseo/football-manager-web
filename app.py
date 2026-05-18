import os
import random

from flask import Flask, jsonify, render_template, request

from config import config
from game_engine import League, MatchSimulator, TACTICS
from player import Player, Position
from team import Team


FORMATIONS = {"4-3-3", "4-2-4", "3-5-2", "5-3-2"}


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
        player_team = create_team("FC Codex")
        cpu_teams = [
            create_team("Seoul Rangers"),
            create_team("Busan Waves"),
            create_team("Incheon United"),
            create_team("Daegu Falcons"),
        ]
        league = League([player_team, *cpu_teams])
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
    positions = [Position.GK, *([Position.DEF] * 4), *([Position.MID] * 3), *([Position.FWD] * 3)]
    first_names = ["민준", "서준", "도윤", "시우", "하준", "주원", "지호", "도현", "준서", "건우", "현우"]
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한"]

    for index, position in enumerate(positions):
        player_name = f"{last_names[index]}{first_names[index]}"
        overall = random.randint(64, 90)
        team.add_player(Player(player_name, position, overall))

    return team


if __name__ == "__main__":
    app = create_app("development")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
