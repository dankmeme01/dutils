from .classes.locstrings import *
from .classes.brawlers import *
from .classes.tourneys import *
from .classes.exceptions import *
from .classes.boxes import *
from .classes.server import *
from difflib import SequenceMatcher
from pathlib import Path
try:
    import simplejson as json
except ModuleNotFoundError:
    import json

__initialized__ = [False, False]
__init_data__ = None

datapath = Path(__file__).parent / "data"
assetpath = Path(__file__).parent / "assets"
logpath = Path(__file__).parent / "logs"
logpath.mkdir(exist_ok=True)

with open(datapath / "brawlers.json", "rb") as f:
    _bjson = json.load(f)
    f.close()
with open(datapath / "locales.json", "rb") as f:
    _ljson = json.load(f)
    f.close()
with open(datapath / "strings.json", "rb") as f:
    _sjson = json.load(f)
    f.close()


def pre_init(season: int = calc_season(), locale: str = 'en') -> None:
    global __initialized__, __init_data__
    if __initialized__[0] or __initialized__[1]:
        raise AlreadyInitialized("Module is already pre-initialized.")
    __initialized__ = [True, False]
    __init_data__ = {"season": season, "locale": locale}

def init() -> None:
    global __initialized__, __init_data__
    if __initialized__[1]:
        raise AlreadyInitialized("Module is already initialized.")
    elif not __initialized__[0]:
        raise NotInitialized("Module is not pre-initialized.")

    change_lang(__init_data__["locale"])
    __initialized__[1] = True

def change_lang(locale):
    global __init_data__, brawlers
    __init_data__["locale"] = locale

    loc = LocalizationManager.from_obj(_ljson, _sjson)
    _tr = lambda key: loc.get(key).get(__init_data__["locale"])

    brawlers = []
    for b in _bjson:
        season = b["season"]

        brawlers.append(
            Brawler(
                rarity=adjust_chroma(__init_data__["season"], season, Rarity(b["rarity"])),
                name=parse_str_fun(b["name"], _tr), # Replace {placeholders} with Names
                icon_path=assetpath / (b["imgc"] + "_i.png"),
                like_path=assetpath / (b["imgc"] + "_l.png"),
                season=season
            )
        )

def search_brawlers(querytype: BrawlerQuery, all_list: list[Brawler], query, threshold=0.6):
    results = []
    match querytype:
        case BrawlerQuery.SEASON:
            for b in all_list:
                if b.season == query: results.append(b)
        case BrawlerQuery.NAME:
            for b in all_list:
                res = SequenceMatcher(None, b.name.lower(), query.strip().lower()).ratio()
                if res >= threshold:
                    results.append(b)
        case BrawlerQuery.RARITY:
            for b in all_list:
                if b.rarity == query: results.append(b)
                elif query == Rarity.CHROMA and (14 <= b.rarity.value <= 16): results.append(b)
        case _:
            raise ValueError("Invalid query type: %s" % querytype.__class__.__name__)
    return results

def search_brawler(querytype: BrawlerQuery, all_list: list[Brawler], query, threshold=0.6):
    results = search_brawlers(querytype, all_list, query, threshold)
    if not results: return None
    return results[0]