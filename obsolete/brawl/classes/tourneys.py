from dataclasses import dataclass
from enum import Enum
from pathlib import Path

@dataclass
class Player:
    name: str
    tag: str
    total_trophies: int
    xp_level: int
    club_name: str

@dataclass
class Team:
    players: list[Player]
    name: str

class Mode(Enum):
    GEMGRAB = 1
    BRAWLBALL = 2
    HEIST = 3
    BOUNTY = 4
    HOTZONE = 5
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

@dataclass
class Map:
    mode: Mode
    name: str
    id: str
    map_view: Path

class Tournament:
    def __init__(self, teams: list):
        self.teams = teams
