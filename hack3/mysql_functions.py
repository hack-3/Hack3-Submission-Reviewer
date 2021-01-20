from typing import List
import mysql.connector
from mysql.connector import cursor
from datetime import datetime
from hack3.Config import Config


def get_connection() -> mysql.connector:
    """
    Returns a connection to a server
    :return: mysql.connector
    """

    config = Config()

    return mysql.connector.connect(
        user=config.user, password=config.password,
        host=config.host,
        database="hack3"
    )


def store_into_projects(curs: cursor.MySQLCursor, url: str, desc_hash: str) -> None:
    """
    Stores an entry into the projects table
    :param curs: The cursor so we can open/close things outside of function
    :param url: Url of project
    :param desc_hash: Description Hash
    :return: None
    """
    try:
        curs.execute(
            f"INSERT IGNORE INTO projects (url, timeAdded, descHash) VALUES ('{url}', '{datetime.today()}', '{desc_hash}');")
    except Exception as e:
        print(e)


def store_into_files(curs: cursor.MySQLCursor, url: str, file_hash: str, extension: str) -> None:
    """
    Stores a file into the "files" table
    :param curs: The cursor so we can open/close things outside of function
    :param url: Url of project
    :param file_hash: File hash
    :param extension: File extension
    :return: None
    """
    try:
        curs.execute(
            f"INSERT IGNORE INTO files (url, timeAdded, fileHash, extension) VALUES ('{url}', '{datetime.today()}', '{file_hash}', '{extension}');")
    except Exception as e:
        print(e)


def get_unadded_urls(curs: cursor.MySQLCursor) -> List[str]:
    """
    Gets the urls from projects table that haven't been added to the files table
    :param curs: The cursor so we can open/close things outside of function
    :return: List of urls
    """
    curs.execute("SELECT url FROM projects WHERE url NOT IN (SELECT url FROM files);")
    return [i[0] for i in curs]
