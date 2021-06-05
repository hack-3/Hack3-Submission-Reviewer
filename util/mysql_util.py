from typing import List, Tuple, Optional
import mysql.connector
from mysql.connector import cursor, errors
from datetime import datetime
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


def command(command: str, curs: Optional[cursor.MySQLCursor] = None):
    to_close = False
    connection = None

    if not curs:
        connection = connect_database()
        curs = connection.cursor()
        to_close = True

    try:
        to_return = curs.execute(command)
    except Exception as e:
        print(e)
        to_return = None

    if to_close:
        connection.commit()

        curs.close()
        connection.close()

    return to_return


def insert_values(table: str, curs: Optional[cursor.MySQLCursor] = None, **kwargs):
    params = ", ".join(map(lambda x: f"'{x}'", kwargs.keys()))
    values = ", ".join(map(lambda x: f"'{x}'", kwargs.keys()))

    command(f"INSERT IGNORE INTO {table} ({params}) VALUES ({values});", curs=curs)


def create_table(table_name: str, curs: Optional[cursor.MySQLCursor] = None, override=False, **kwargs: DataType):
    categories = ", ".join(map(lambda x: f"{x} {str(kwargs[x])}", kwargs))

    # print(f"CREATE TABLE{'' if override else 'IF NOT EXISTS '} {table_name} ({categories})")

    command(f"CREATE TABLE {'' if override else 'IF NOT EXISTS '}{table_name} ({categories})", curs=curs)


def get_values(table: str, *categories: str, restrictions: list = None, curs: Optional[cursor.MySQLCursor] = None):
    if not restrictions:
        restrictions = []

    temp1 = ", ".join(categories)
    temp2 = "WHERE" if restrictions else "" + " AND ".join(restrictions)

    return command(f"SELECT {temp1} FROM {table} {temp2}", curs=curs)
