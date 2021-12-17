from classes.locstrings import *
from classes.brawlers import *
from classes.tourneys import *
from classes.exceptions import *
from classes.boxes import *
import simplejson as json
from pathlib import Path

__initialized__ = [False, False]
__init_data__ = None

def pre_init(season: int = calc_season(), locale: str = 'en') -> None:
    global __initialized__, __init_data__
    if __initialized__[0] or __initialized__[1]:
        raise AlreadyInitialized("Module is already pre-initialized.")
    __initialized__ = [True, False]
    __init_data__ = {"season": season, "locale": locale}

def init() -> None:
    global __initialized__, __init_data__, brawlers, _tr
    if __initialized__[1]:
        raise AlreadyInitialized("Module is already initialized.")
    elif not __initialized__[0]:
        raise AlreadyInitialized("Module is not pre-initialized.")

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
