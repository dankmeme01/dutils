from dataclasses import dataclass
from json import loads
from typing import Optional, Any
from datetime import datetime
from dutils.util import in_between
from enum import Enum, auto
import pytz


def parse_time(time: str) -> datetime:
    # example : 20211228T101928.000Z
    dt = datetime.strptime(time, '%Y%m%dT%f.000Z')
    dtp = datetime(dt.year, dt.month, dt.day, tzinfo=pytz.timezone('ZULU'))
    return dtp

class Mode(Enum):
    GEMGRAB = auto()
    SHOWDOWN = auto()
    BRAWLBALL = auto()
    DUELS = auto()
    POWER_LEAGUE = auto()
    HEIST = auto()
    KNOCKOUT = auto()
    BOUNTY = auto()
    HOTZONE = auto()
    SIEGE = auto()

class MatchType(Enum):
    RANKED = auto()
    POWER_LEAGUE = auto()
    CLUB_LEAGUE = auto()
    MAP_MAKER = auto()

class GameResult(Enum):
    VICTORY = auto()
    LOSS = auto()
    DRAW = auto()

@dataclass
class Event:
    mode: Optional[str]
    id_: int
    map: Any

    start_time: Optional[str]
    end_time: Optional[str]

    @classmethod
    def from_json(cls, json: str):
        return cls(
            mode=json.get("mode", None),
            id_=json.get("id", None),
            map=json.get("map", None),
            start_time=json.get("startTime", None),
            end_time=json.get("endTime", None)
        )

@dataclass
class PersonalBrawlerData:
    id_: int
    name: str
    power: int
    trophies: int

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None

        return cls(
            id_=json["id"],
            name=json["name"],
            power=json["power"],
            trophies=json["trophies"]
        )

@dataclass
class Equippable:
    id_: int
    name: str

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None

        return cls(id_=json['id'], name=json['name'])

@dataclass
class PersonalBrawler:
    id_: int
    name: str
    power: int
    rank: int
    trophies: int
    highest_trophies: int

    gears: list[Equippable]
    gadgets: list[Equippable]
    star_powers: list[Equippable]

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None

        return cls(
            id_=json['id'],
            name=json['name'].lower().capitalize(),
            power=json['power'],
            rank=json['rank'],
            trophies=json['trophies'],
            highest_trophies=json['highestTrophies'],
            gears=[Equippable.from_json(x) for x in json['gears']],
            gadgets=[Equippable.from_json(x) for x in json['gadgets']],
            star_powers=[Equippable.from_json(x) for x in json['starPowers']]
        )

@dataclass
class Brawler:
    name: str
    id_: int
    gadgets: list[Equippable]
    star_powers: list[Equippable]

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None

        return cls(
            id_=json['id'],
            name=json['name'],
            gadgets=[Equippable.from_json(x) for x in json['gadgets']],
            star_powers=[Equippable.from_json(x) for x in json['starPowers']]
        )

@dataclass
class GamePlayer:
    tag: str
    name: str
    brawler: PersonalBrawlerData

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None

        return cls(
            tag=json["tag"],
            name=json["name"],
            brawler=PersonalBrawlerData.from_json(json["brawler"])
        )

Team = list[GamePlayer]

@dataclass
class ClubMember:
    icon_id: int
    tag: str
    name: str
    trophies: int
    role: str
    name_color: str

    @classmethod
    def from_json(cls, json):
        return cls(
            icon_id=json['icon']['id'],
            tag=json['tag'],
            name=json['name'],
            trophies=json['trophies'],
            role=json['role'],
            name_color=json['nameColor']
        )

@dataclass
class Club:
    tag: str
    name: str
    description: str
    trophies: int
    required_trophies: int
    type_: str
    badge_id: int
    members: list[ClubMember]

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None

        return cls(
            tag=json["tag"],
            name=json["name"],
            description=json["description"],
            trophies=json['trophies'],
            required_trophies=json['requiredTrophies'],
            type_=json['type'],
            badge_id=json['badgeId'],
            members=[ClubMember.from_json(x) for x in json['members']]
        )

@dataclass
class ClubData:
    tag: str
    name: str

@dataclass
class Player:
    tag: str
    name: str
    namecolor: str # Hex
    iconid: int

    trophies: int
    highest_trophies: int
    xplevel: int
    xp_points: int

    qualified_from_championship_challenge: bool

    victories_3v3: int
    victories_solo: int
    victories_duo: int

    best_robo_rumble: int
    best_big_brawler: int

    club: ClubData
    brawlers: list[Brawler]

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None

        return cls(
            tag=json['tag'],
            name=json['name'],
            namecolor=json['nameColor'],
            iconid=json['icon']['id'],
            trophies=json['trophies'],
            highest_trophies=json['highestTrophies'],
            xplevel=json['expLevel'],
            xp_points=json['expPoints'],
            qualified_from_championship_challenge=json['isQualifiedFromChampionshipChallenge'],
            victories_3v3=json['3vs3Victories'],
            victories_solo=json['soloVictories'],
            victories_duo=json['duoVictories'],
            best_robo_rumble=json['bestRoboRumbleTime'],
            best_big_brawler=json['bestTimeAsBigBrawler'],
            club=ClubData(json['club']['tag'], json['club']['name']),
            brawlers=[PersonalBrawler.from_json(x) for x in json['brawlers']]
        )

@dataclass
class Battle:
    time: datetime
    event: Event
    mode: str # Mode
    type_: str # MatchType
    result: str # GameResult
    duration: int # seconds
    starplayer: GamePlayer
    teams: list[Team]

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None

        battle = json["battle"]
        teams = []
        for t in battle["teams"]:
            # t is a list of players
            teams.append([GamePlayer.from_json(x) for x in t])

        return cls(
            time=parse_time(json["battleTime"]),
            event=Event.from_json(json["event"]),
            mode=battle["mode"],
            type_=battle["type"],
            result=battle.get("result", None),
            duration=battle.get("duration"),
            starplayer=GamePlayer.from_json(battle.get("starPlayer")),
            teams=teams
        )