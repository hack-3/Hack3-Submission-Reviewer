from datetime import datetime
from typing import List, Tuple, Optional
import mysql.connector
from mysql.connector import cursor, errors
from util import configuration as c
import util.mysql_datatypes as DataType


def connect() -> mysql.connector:
    return mysql.connector.connect(
        user=c.get_username(), password=c.get_password(),
        host=c.get_host()
    )


def connect_database() -> mysql.connector:
    return mysql.connector.connect(
        user=c.get_username(), password=c.get_password(),
        host=c.get_host(), database=c.get_database()
    )


def command(command: str, commit=False, curs: Optional[cursor.MySQLCursor] = None):
    to_close = False
    to_return = None
    connection = None

    if not curs:
        connection = connect_database()
        curs = connection.cursor()
        to_close = True

    try:
        curs.execute(command)

        if not commit:
            to_return = curs.fetchall()
    except Exception as e:
        print(e)

    if to_close:
        if commit:
            connection.commit()

        curs.close()
        connection.close()

    return to_return


def insert_values(table: str, curs: Optional[cursor.MySQLCursor] = None, **kwargs):
    params = ", ".join(map(lambda x: f"{x}", kwargs.keys()))
    values = ", ".join(map(lambda x: f"'{x}'", kwargs.values()))

    command(f"INSERT IGNORE INTO {table} ({params}) VALUES ({values});", commit=True, curs=curs)


def create_table(table_name: str, curs: Optional[cursor.MySQLCursor] = None, override=False, **kwargs: DataType):
    categories = ", ".join(map(lambda x: f"{x} {str(kwargs[x])}", kwargs))

    command(f"CREATE TABLE {'' if override else 'IF NOT EXISTS '}{table_name} ({categories})", commit=True, curs=curs)


def update_table(table_name: str, curs: Optional[cursor.MySQLCursor] = None, restrictions: Optional[List] = None,
                 **modified_columns):
    if not restrictions:
        restrictions = []
    temp1 = ", ".join(f"{i}={str(modified_columns[i])}" for i in modified_columns)
    temp2 = ("WHERE " if restrictions else "") + " AND ".join(restrictions)

    command(f"UPDATE {table_name} SET {temp1} {temp2}", commit=True, curs=curs)


def get_values(table: str, *categories: str, restrictions: Optional[List] = None,
               curs: Optional[cursor.MySQLCursor] = None):
    if not restrictions:
        restrictions = []

    temp1 = ", ".join(categories)
    temp2 = ("WHERE " if restrictions else "") + " AND ".join(restrictions)

    return command(f"SELECT {temp1} FROM {table} {temp2}", curs=curs)


def store_devpost_project(devpost_url: str, github_sources: str, desc_hash: str):
    insert_values("projects", devpostUrl=devpost_url, githubSources=github_sources, timeAdded=datetime.today(),
                  descHash=desc_hash)


def store_file(devpost_url: str, file_hash: str, file_name: str, file_extension: str):
    create_table(file_extension, devpostUrl=DataType.VarChar(120), fileHash=DataType.VarChar(100),
                 fileName=DataType.VarChar(30), timeAdded=DataType.DateTime())
    insert_values(file_extension, devpostUrl=devpost_url, fileHash=file_hash, fileName=file_name,
                  timeAdded=datetime.today())


def mark_project_checked(devpost_url: str):
    update_table("projects", restrictions=[f"devpostUrl='{devpost_url}'"], added=DataType.Bool(True))


def get_unadded_projects() -> List[Tuple[str, str]]:
    return get_values("projects", "devpostUrl", "githubSources", restrictions=["added = FALSE"])


def is_project_added(devpost_url) -> bool:
    return bool(get_values("projects", "added", restrictions=["added = FALSE", f"devpostUrl = '{devpost_url}'"]))


def get_desc_hashes() -> List[Tuple[str, str]]:
    return get_values("projects", "devpostUrl", "descHash")


def get_file_hashes(file_ext: str) -> List[Tuple[str, str, str]]:
    return get_values(file_ext, "devpostUrl", "fileName", "fileHash")
