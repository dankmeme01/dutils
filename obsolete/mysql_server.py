import mysql.connector
from enum import Enum, auto

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
    JSON =       auto()

class Constraints(Enum):
    NOT_NULL = 0b00001
    UNIQUE = 0b00010
    CHECK = 0b00100
    AUTO_INCREMENT = 0b01000
    PRIMARY_KEY = 0b10000

class Column:
    def __init__(self, name: str, type: Types, constraints: list[Constraints] = [], size=None, default=None):
        self.name = name
        self.type = type
        self.constraints = constraints
        self.size = size
        self.default = default

    def __str__(self):
        if not self.constraints:
            cstr = ""
        else:
            cstr = " " + " ".join([x.name.replace("_", " ") for x in self.constraints])
        typestr = self.type.name if not self.size else f"{self.type.name}({self.size})"
        if self.default is None:
            return f"`{self.name}` {typestr}{cstr}"
        else:
            if isinstance(self.default, str):
                ttdef = f'"{self.default}"'
            elif isinstance(self.default, bool):
                ttdef = str(self.default).upper()
            else:
                ttdef = str(self.default)
            return f"`{self.name}` {typestr}{cstr} DEFAULT {ttdef}"

class Schema:
    def __init__(self, table_name: str):
        self.name = table_name
        self.columns: list[Column] = []
        self.foreigns: list[str] = []
        self.primary: Column = None

    def add(self, name: str, type_: Types, constraints: list[Constraints] = [], size=None, default=None):
        self.columns.append(Column(name, type_, constraints, size, default))
        return self

    def add_foreign(self, name: str, type_: Types, ref_table_name: str, ref_table_col: str, size=None):
        self.columns.append(Column(name, type_, [], size))
        self.foreigns.append(f"FOREIGN KEY({name}) REFERENCES {ref_table_name}({ref_table_col})")
        return self

    def set_primary(self, name: str, type_: Types, constraints: list[Constraints] = [], size=None, autoincrement=False):
        self.add(name, type_, constraints + [Constraints.PRIMARY_KEY] + ([Constraints.AUTO_INCREMENT] if autoincrement else []), size)
        return self

    def __str__(self):
        rows = ",\n".join([str(x) for x in self.columns])
        if self.foreigns:
            rows += ",\n"
            foreigns = ",\n".join([str(x) for x in self.foreigns])
        else:
            foreigns = ""
        return f"""CREATE TABLE IF NOT EXISTS {self.name} (
            {rows}{foreigns}
            ) ENGINE = InnoDB""".replace("    ", "")

# Main database
class Server:
    def __init__(self,
                 host: str = "localhost",
                 username: str = "root",
                 password: str = "",
                 db_name: str = "",
                 no_raise: bool = False) -> None:
        self.no_raise = no_raise
        self.conn = mysql.connector.connect(
            host=host,
            user=username,
            passwd=password
        )

        self.execute_query("CREATE DATABASE IF NOT EXISTS " + db_name)
        self.conn.close()

        self.conn = mysql.connector.connect(
            host=host,
            user=username,
            passwd=password,
            database=db_name
        )

    def execute_query(self, query: str, get_results: bool = False, **kw):
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

    def add_table(self, schema: Schema):
        try:
            self.execute_query(str(schema))
        except mysql.connector.Error as e:
            print(f"Error: {e}. Table schema:")
            print(schema)

    def insert(self, table_name: str, **kwargs):
        # confusing but i never cared
        self.execute_query(f"""INSERT INTO {table_name} ({', '.join(list(kwargs.keys()))})
        VALUES ({', '.join([f'"{x}"' if isinstance(x, str) and x != "NOW()" else str(x) for x in list(kwargs.values())])})""")

    def update(self, table_name: str, where_cond: str, **kwargs):
        self.execute_query(f"""UPDATE {table_name} SET
        {', '.join([f'`{k}` = ' + (f"'{v}'" if isinstance(v, str) else str(v)) for k,v in kwargs.items()])}
        WHERE {where_cond}""")

    def select(self, table_name: str, *columns, where_cond: str=None, limit: int=None, results=False):
        if not columns:
            colexp = "*"
        else:
            colexp = f"({', '.join(columns)})"

        if not where_cond:
            whexp = ""
        else:
            whexp = f"WHERE {where_cond}"

        if not limit:
            limexp = ""
        else:
            limexp = f"LIMIT {limit}"

        q = f"SELECT {colexp} FROM {table_name} {whexp} {limexp}"
        return self.execute_query(q, results)

    def drop(self, table_name: str):
        self.execute_query(f"DROP TABLE {table_name}")