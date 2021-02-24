from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List
from enum import Enum


@dataclass_json
@dataclass
class Game:
    """
    {
      "id": "totally-unique-game-id",
      "timeout": 500
    }
    """
    id: str
    timeout: str

@dataclass_json
@dataclass
class Cell:
    x: int
    y: int

    def __hash__(self):
        return hash(self.x * 10000000 + self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        if self.x == other.x:
            return self.y < other.y
        else:
            return self.x < other.x

@dataclass_json
@dataclass
class RankedCell:
    cell: Cell
    rank: int = 0

    def __hash__(self):
        return hash(self.cell.x * 10000000 + self.cell.y)

    def __eq__(self, other):
        return self.cell.x == other.x and self.cell.y == other.y

    def __lt__(self, other):
        return self.rank < other.rank


@dataclass_json
@dataclass
class BattleSnake:
    """
    {
      "id": "totally-unique-snake-id",
      "name": "Sneky McSnek Face",
      "health": 54,
      "body": [
        {"x": 0, "y": 0},
        {"x": 1, "y": 0},
        {"x": 2, "y": 0}
      ],
      "latency": "123",
      "head": {"x": 0, "y": 0},
      "length": 3,
      "shout": "why are we shouting??",
      "squad": "1"
    }
    """
    id: str
    name: str
    health: int
    body: List[Cell]
    latency: str
    head: Cell
    length: int
    shout: str
    squad: str = ''


@dataclass_json
@dataclass
class Board:
    """
    {
      "height": 11,
      "width": 11,
      "food": [
        {"x": 5, "y": 5},
        {"x": 9, "y": 0},
        {"x": 2, "y": 6}
      ],
      "hazards": [
        {"x": 0, "y": 0},
        {"x": 0, "y": 1},
        {"x": 0, "y": 2}
      ],
      "snakes": [
        {"id": "snake-one", ... },
        {"id": "snake-two", ... },
        {"id": "snake-three", ... }
      ]
    }
    """
    height: int
    width: int
    food: List[Cell]
    hazards: List[Cell]
    snakes: List[BattleSnake]


@dataclass_json
@dataclass
class MovePostRequest:
    game: Game
    turn: int
    board: Board
    you: BattleSnake


class Move(Enum):
    up = "up"
    down = "down"
    left = "left"
    right = "right"
