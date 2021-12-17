from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field as dc_field
from . import locstrings
from datetime import datetime

class Rarity(Enum):
    TROPHYROAD = 1
    RARE = 2
    VERYRARE = 3
    EPIC = 4
    MYTHIC = 5
    LEGENDARY = 6

    CHROMA = 7
    CHROMA_EPIC = 4
    CHROMA_MYTHIC = 5
    CHROMA_LEGENDARY = 6

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

@dataclass
class Brawler:
    rarity: Rarity
    name: locstrings.LocalizationString
    season: int = dc_field(repr=False)
    icon_path: Path = dc_field(repr=False)
    like_path: Path = dc_field(repr=False)

def adjust_chroma(cur_season: int, season_added: int, rarity: Rarity) -> Rarity:
    if rarity != Rarity.CHROMA:
        return rarity

    diff = cur_season - season_added
    rarity = Rarity.LEGENDARY.value - diff
    match rarity:
        case 6:
            return Rarity.CHROMA_LEGENDARY
        case 5:
            return Rarity.CHROMA_MYTHIC
        case _:
            return Rarity.CHROMA_EPIC

def calc_season(date: datetime.datetime = datetime.datetime.now()):
    return 9 # TODO