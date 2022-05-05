from ..util.client import BaseClient
from ..util.endpoints import OfficialEndpoints as Endpoints
from .models import *

BASE = "https://api.brawlstars.com/v1"
BASE_PROXY = "https://bsproxy.royaleapi.dev/v1"

class Client(BaseClient):
    def __init__(self, token: str, use_proxy: bool = True):
        base = BASE_PROXY if use_proxy else BASE
        super().__init__(token, base)

    def _check_tag(self, tag: str):
        if not tag.startswith("#"):
            tag = "#" + tag

        return tag

    def get_battle_log(self, playertag: str) -> list[Battle]:
        tag = self._check_tag(playertag)
        r = self._get(Endpoints.BATTLE_LOG % tag)
        battles = r["items"]
        return [Battle.from_json(b) for b in battles]

    def get_player(self, playertag: str) -> Player:
        tag = self._check_tag(playertag)
        r = self._get(Endpoints.PLAYER % tag)
        return Player.from_json(r)

    def get_club_members(self, clubtag: str) -> list[ClubMember]:
        tag = self._check_tag(clubtag)
        r = self._get(Endpoints.CLUB_MEMBERS % tag)
        members = r['items']
        return [ClubMember.from_json(c) for c in members]

    def get_club(self, clubtag: str) -> Club:
        tag = self._check_tag(clubtag)
        r = self._get(Endpoints.CLUB % tag)
        return Club.from_json(r)

    def get_brawlers(self) -> list[Brawler]:
        r = self._get(Endpoints.BRAWLERS)
        brawlers = r['items']
        return [Brawler.from_json(b) for b in brawlers]

    def get_brawler(self, brawlerid: int) -> Brawler:
        r = self._get(Endpoints.BRAWLER % brawlerid)
        return Brawler.from_json(r)

    def get_event_rotation(self) -> Event:
        r = self._get(Endpoints.EVENTS)
        return [Event.from_json(e) for e in r]