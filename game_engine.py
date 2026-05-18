import random


TACTICS = {
    "balanced": {"label": "균형", "attack": 0.0, "defense": 0.0},
    "attacking": {"label": "공격", "attack": 0.45, "defense": -0.25},
    "defensive": {"label": "수비", "attack": -0.25, "defense": 0.45},
}


class MatchSimulator:
    @staticmethod
    def simulate_match(home_team, away_team) -> tuple[int, int]:
        home_attack = home_team.get_team_strength() * 1.04
        away_attack = away_team.get_team_strength()
        home_goals = MatchSimulator.calculate_goals(home_attack, away_attack, home_team.tactics)
        away_goals = MatchSimulator.calculate_goals(away_attack, home_attack, away_team.tactics)
        return home_goals, away_goals

    @staticmethod
    def calculate_goals(team_strength: float, opponent_strength: float, tactics: str) -> int:
        tactic = TACTICS.get(tactics, TACTICS["balanced"])
        opponent_tactic = max(opponent_strength, 1)
        strength_ratio = team_strength / opponent_tactic
        expected_goals = 1.35 + (strength_ratio - 1) * 1.2 + tactic["attack"]
        goals = random.gauss(expected_goals, 0.85)
        return max(0, min(7, int(round(goals))))

    @staticmethod
    def update_standings(home_team, away_team, home_goals: int, away_goals: int) -> str:
        home_team.goals_for += home_goals
        home_team.goals_against += away_goals
        away_team.goals_for += away_goals
        away_team.goals_against += home_goals

        if home_goals > away_goals:
            home_team.wins += 1
            away_team.losses += 1
            return "win"
        if home_goals < away_goals:
            home_team.losses += 1
            away_team.wins += 1
            return "loss"

        home_team.draws += 1
        away_team.draws += 1
        return "draw"


class League:
    def __init__(self, teams):
        self.teams = teams
        self.match_history = []
        self.current_week = 1

    def get_standings(self):
        return sorted(
            self.teams,
            key=lambda team: (
                team.get_points(),
                team.get_goal_diff(),
                team.goals_for,
                team.get_team_strength(),
            ),
            reverse=True,
        )

    def get_standings_dict(self) -> list[dict]:
        return [
            {
                "rank": index + 1,
                "team_name": team.name,
                "matches": team.get_matches_played(),
                "wins": team.wins,
                "draws": team.draws,
                "losses": team.losses,
                "goals_for": team.goals_for,
                "goals_against": team.goals_against,
                "goal_diff": team.get_goal_diff(),
                "points": team.get_points(),
            }
            for index, team in enumerate(self.get_standings())
        ]

    def record_match(self, home_team, away_team, home_goals: int, away_goals: int, result: str) -> dict:
        match_info = {
            "week": self.current_week,
            "home_team": home_team.name,
            "away_team": away_team.name,
            "home_goals": home_goals,
            "away_goals": away_goals,
            "result": result,
        }
        self.match_history.append(match_info)
        self.current_week += 1
        return match_info
