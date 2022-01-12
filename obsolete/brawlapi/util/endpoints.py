class OfficialEndpoints:
    BATTLE_LOG = "/players/%s/battlelog" # Get log of recent battles for a player.
    PLAYER = "/players/%s" # Get player information
    CLUB_MEMBERS = "/clubs/%s/members" # List club members.
    CLUB = "/clubs/%s" # Get club information.
    BRAWLERS = "/brawlers" # Get list of available brawlers.
    BRAWLER = "/brawlers/%s" # Get information about a brawler.
    EVENTS = "/events/rotation" # Get event rotation

    TOP_PLAYERS = "/rankings/%s/players" # Get player rankings for a country or global rankings.
    TOP_BRAWLERS = "/rankings/%s/brawlers/%s" # Get brawler rankings for a country or global rankings.
    TOP_CLUBS = "/rankings/%s/clubs" # Get club rankings for a country or global rankings.
    TOP_PL_SEASONS = "/rankings/%s/powerplay/seasons" # Get list of power play seasons for a country or global rankings.
    TOP_PL_SEASON = "/rankings/%s/powerplay/seasons/%s" # Get power play rankings for a country or global rankings.