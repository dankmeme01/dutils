# pip install mysql-connector-python
import mysql.connector
import time, random
from enum import Enum, auto
from dutils.obsolete.brawl.classes.brawlers import Brawler, Rarity
from dataclasses import dataclass

class Types(Enum):
    CHAR =       auto()
    VARCHAR =    auto()
    TINYTEXT =   auto()
    TEXT =       auto()
    BLOB =       auto()
    MEDIUMTEXT = auto()
    MEDIUMBLOB = auto()
    LONGTEXT =   auto()
    LONGBLOB =   auto()
    TINYINT =    auto()
    SMALLINT =   auto()
    MEDIUMINT =  auto()
    INT =        auto()
    BIGINT =     auto()
    FLOAT =      auto()
    DOUBLE =     auto()
    DECIMAL =    auto()
    DATE =       auto()
    DATETIME =   auto()
    TIMESTAMP =  auto()
    TIME =       auto()
    ENUM =       auto()
    SET =        auto()
    BOOLEAN =    auto()

class Constraints(Enum):
    NOT_NULL = 0b00000001
    UNIQUE = 0b00000010
    PRIMARY_KEY = 0b00000100
    FOREIGN_KEY = 0b00001000
    CHECK = 0b00010000
    DEFAULT = 0b00100000
    AUTO_INCREMENT = 0b01000000

ACC_DATA_SCHEMA = {
    "dc_uid": (Types.BIGINT, [Constraints.NOT_NULL, Constraints.UNIQUE]),
    "nickname": (Types.TINYTEXT, [Constraints.NOT_NULL]),
    "playertag": (Types.TEXT, [Constraints.NOT_NULL, Constraints.UNIQUE]),
    "registered": (Types.BIGINT,),
    "trophies": (Types.INT,),
    "__primary_key__": "dc_uid"
}

INVENTORY_SCHEMA = {
    "coins": (Types.INT,),
    "gems": (Types.INT,),
    "starpoints": (Types.INT,),
    "dc_uid": (Types.BIGINT, [Constraints.NOT_NULL, Constraints.UNIQUE]),

    "scrap": (Types.INT,),
    "geardmg": (Types.INT,),
    "gearshield": (Types.INT,),
    "__foreign_keys__": {
        "dc_uid": "users(dc_uid)"
    }
}

# The brawlers are formatted like this example:
# Shelly with power 11, 0 power points, 578 trophies, first gadget, no second g, no first sp, second sp, first gadget chosen, second sp chosen, gear1 shield lv3, gear2 damage lv2
# 11|0|578|1|0|0|1|1|2|3|2
# El primo not unlocked
# 0|0|0|0|0|0|0|0|0|0|0
# Nita power 3, 41 pp, 53 trophies, no gadget 1, 2, no sp 1, 2, no chosen, no chosen, no gear, no gear
# 3|41|53|0|0|0|0|0|0|0|0

BRAWLERS_SCHEMA = {
    "dc_uid": (Types.BIGINT, [Constraints.NOT_NULL, Constraints.UNIQUE]),
    # will be filled up later in the code
    "__foreign_keys__": {
        "dc_uid": "users(dc_uid)"
    }
}

@dataclass
class BrawlerDB:
    name: str
    rarity: Rarity
    power: int
    power_points: int
    trophies: int
    gadget1: bool
    gadget2: bool
    sp1: bool
    sp2: bool
    chosen_g: int
    chosen_sp: int
    gear_shield: int
    gear_damage: int

@dataclass
class PlayerData:
    name: str
    tag: str
    registered: str
    trophies: int
    coins: int
    star_points: int
    gems: int
    scrap: int
    gear_dmg_tokens: int
    gear_shield_tokens: int
    brawlers: list[BrawlerDB]

# Main database
class Server:
    def __init__(self, brawlers: list[Brawler], season, host: str = "localhost", username: str = "root", password: str = "", no_raise=False) -> None:
        """Initialize the server, connect to the MySQL database and create the table if needed.

        Args:
            brawlers (list[Brawler]): List of all available brawlers.
            season (int): Current season.
            host (str, optional): Hostname of the remote MySQL server. Defaults to "localhost".
            username (str, optional): Username for authenticating to the MySQL server. Defaults to "root".
            password (str): Password for authenticating to the MySQL server.
            no_raise (bool, optional): Defines whether the server should raise an error on unsuccessful query. Defaults to False
        """

        global BRAWLERS_SCHEMA

        self.no_raise = no_raise
        self.brawlers = brawlers
        self.season = season
        self.brquery = self.get_brawler_query()
        for b in self.brawlers:
            BRAWLERS_SCHEMA[b.name.lower().replace('-','').replace('.','').replace(' ', '')] = (Types.TEXT,)
        self.conn = mysql.connector.connect(
            host=host,
            user=username,
            passwd=password
        )

        self.execute_query("CREATE DATABASE IF NOT EXISTS brawl_db")
        self.conn.close()

        self.conn = mysql.connector.connect(
            host=host,
            user=username,
            passwd=password,
            database="brawl_db"
        )

        self.create_table("users", ACC_DATA_SCHEMA)
        self.create_table("inventory", INVENTORY_SCHEMA)
        self.create_table("brawlers", BRAWLERS_SCHEMA)
        print("Connection to the database successful.")

    def execute_query(self, query: str, get_results: bool = False, **kw) -> None:
        """Execute a MySQL query.

        Args:
            query (str): The query to execute.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, **kw)
                if get_results:
                    return cursor.fetchall()
            self.conn.commit()
        except mysql.connector.Error as e:
            if self.no_raise:
                print(f"Error happened while executing query: {str(e)}")
            else:
                raise e

    def create_table(self, name: str, schema: dict) -> None:
        """Create a table with name and schema.

        Args:
            name (str): The name of the table to create.
            schema (dict): The schema to use. An example is the ACC_DATA_SCHEMA object.
        """
        query = f"""CREATE TABLE IF NOT EXISTS {name} ("""

        for k, v in schema.items():
            if k.startswith("__"):
                continue

            query += f"\n{k} {v[0].name}"
            val = 0
            if len(v) > 1:
                for x in v[1]: val += x.value
                for c in Constraints:
                    if val & c.value:
                        query += " " + c.name.replace("_", " ")
            query += ","

        if "__foreign_keys__" in schema:
            for k, v in schema["__foreign_keys__"].items():
                query += f"\nFOREIGN KEY({k}) REFERENCES {v}"

        if "__primary_key__" in schema:
            query += f"\nPRIMARY KEY ({schema['__primary_key__']})"

        query += "\n) ENGINE = InnoDB"
        self.execute_query(query)

    def register_user(self, name: str, userid: int) -> None:
        """Register a user in the database.

        Args:
            name (str): The name of registered user.
            userid (int): The unique Discord user ID of the user.
        """
        tag = self.random_tag()
        self.execute_query(
            f"""
            INSERT INTO users (dc_uid, nickname, registered, playertag, trophies)
            VALUES ({userid}, "{name}", {int(time.time())}, "{tag}", 0)
            """
        )

        self.execute_query(
            f"""
            INSERT INTO inventory (coins, gems, starpoints, scrap, geardmg, gearshield, dc_uid)
            VALUES (0, 0, 0, 0, 0, 0, {userid})
            """
        )

        self.execute_query(self.brquery % userid)

    def random_tag(self) -> str:
        """Generate a random player tag (values from '0x1000000000' to '0xffffffffff').

        Returns:
            str: The unique player tag.
        """
        num = random.randint(16 ** 7, 16 ** 8 - 1)
        return hex(num)[2:]

    def make_bdata(self,
                   power: int,
                   power_points: int,
                   trophies: int,
                   gadget1: bool,
                   gadget2: bool,
                   sp1: bool,
                   sp2: bool,
                   gadget_chosen: int,
                   sp_chosen: int,
                   gear1_level: int,
                   gear2_level: int
                   ):
        return f"{power}| \
                 {power_points}| \
                 {trophies}| \
                 {int(gadget1)}| \
                 {int(gadget2)}| \
                 {int(sp1)}| \
                 {int(sp2)}| \
                 {gadget_chosen}| \
                 {sp_chosen}| \
                 {gear1_level}| \
                 {gear2_level}"

    def get_brawler_query(self):
        # i hate myself
        brquery = f"""INSERT INTO brawlers (dc_uid, shelly, {', '.join([b.name.lower().replace('-','').replace('.','').replace(' ', '') for b in self.brawlers[1:]])}) VALUES (%s, "1|0|0|0|0|0|0|0|0|0|0", "{'", "'.join(['0|0|0|0|0|0|0|0|0|0|0' for b in self.brawlers[1:]])}");\n"""

        return brquery

    def get_player_data(self, userid: int) -> PlayerData:
        user_q = self.execute_query(f"SELECT * FROM users WHERE dc_uid = \"{userid}\"", get_results=True)
        inv_q = self.execute_query(f"SELECT * FROM inventory WHERE dc_uid = \"{userid}\"", get_results=True)
        brl_q = self.execute_query(f"SELECT * FROM brawlers WHERE dc_uid = \"{userid}\"", get_results=True)

        if not user_q or not inv_q or not brl_q:
            return None

        user = user_q[0]
        inv = inv_q[0]
        brl = brl_q[0][1:]

        brawlers = []
        i = 0
        while i < len(self.brawlers):
            br_game = self.brawlers[i]
            br_data = [int(x) for x in brl[i].split('|')]
            i += 1
            if br_data[0] < 1: continue
            brawlers.append(BrawlerDB(
                name=br_game.name,
                rarity=br_game.rarity,
                power=br_data[0],
                power_points=br_data[1],
                trophies=br_data[2],
                gadget1=br_data[3],
                gadget2=br_data[4],
                sp1=br_data[5],
                sp2=br_data[6],
                chosen_g=br_data[7],
                chosen_sp=br_data[8],
                gear_shield=br_data[9],
                gear_damage=br_data[10]
            ))
        return PlayerData(
            name=user[1],
            tag=user[2],
            registered=user[3],
            trophies=user[4],
            coins=inv[0],
            gems=inv[1],
            star_points=inv[2],
            scrap=inv[4],
            gear_dmg_tokens=inv[5],
            gear_shield_tokens=inv[6],
            brawlers=brawlers
        )