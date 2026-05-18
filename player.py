from dataclasses import dataclass
from enum import Enum


class Position(Enum):
    GK = "GK"
    DEF = "DEF"
    MID = "MID"
    FWD = "FWD"


@dataclass
class Player:
    name: str
    position: str | Position
    overall: int

    def __post_init__(self) -> None:
        if isinstance(self.position, Position):
            self.position = self.position.value
        self.salary = int(50_000 * (self.overall / 50))
        self.market_value = int(1_000_000 * (self.overall / 50))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "position": self.position,
            "overall": self.overall,
            "salary": self.salary,
            "market_value": self.market_value,
        }
