class Team:
    def __init__(self, name: str, initial_budget: int = 5_000_000):
        self.name = name
        self.budget = initial_budget
        self.players = []
        self.formation = "4-3-3"
        self.tactics = "balanced"
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0

    def add_player(self, player) -> bool:
        if len(self.players) >= 11:
            return False
        self.players.append(player)
        return True

    def get_points(self) -> int:
        return self.wins * 3 + self.draws

    def get_goal_diff(self) -> int:
        return self.goals_for - self.goals_against

    def get_matches_played(self) -> int:
        return self.wins + self.draws + self.losses

    def get_team_strength(self) -> float:
        if len(self.players) < 11:
            return 0.0
        formation_bonus = {
            "4-3-3": 1.02,
            "4-2-4": 1.00,
            "3-5-2": 1.01,
            "5-3-2": 0.99,
        }.get(self.formation, 1.0)
        return (sum(player.overall for player in self.players[:11]) / 11) * formation_bonus

    def reset_record(self) -> None:
        self.wins = self.draws = self.losses = 0
        self.goals_for = self.goals_against = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "budget": self.budget,
            "formation": self.formation,
            "tactics": self.tactics,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "points": self.get_points(),
            "goal_diff": self.get_goal_diff(),
            "matches_played": self.get_matches_played(),
            "team_strength": round(self.get_team_strength(), 1),
            "players": [player.to_dict() for player in self.players],
        }
