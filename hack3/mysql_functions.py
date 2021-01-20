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


def store_into_projects(cursor: cursor.MySQLCursor, url: str, descHash: str) -> None:
    """
    Stores an entry into the projects table
    :param cursor: The cursor so we can open/close things outside of function
    :param url: Url of project
    :param descHash: Description Hash
    :return: None
    """
    try:
        cursor.execute(
            f"INSERT IGNORE INTO projects (url, timeAdded, descHash) VALUES ('{url}', '{datetime.today()}', '{descHash}');")
    except Exception as e:
        print(e)


def store_into_files(cursor: cursor.MySQLCursor, url: str, fileHash: str, extension: str) -> None:
    """
    Stores a file into the "files" table
    :param cursor: The cursor so we can open/close things outside of function
    :param url: Url of project
    :param fileHash: File hash
    :param extension: File extension
    :return: None
    """
    try:
        cursor.execute(
            f"INSERT IGNORE INTO files (url, timeAdded, fileHash, extension) VALUES ('{url}', '{datetime.today()}', '{fileHash}', '{extension}');")
    except Exception as e:
        print(e)


def get_unadded_urls(cursor: cursor.MySQLCursor) -> List[str]:
    """
    Gets the urls from projects table that haven't been added to the files table
    :param cursor: The cursor so we can open/close things outside of function
    :return: List of urls
    """
    cursor.execute("SELECT url FROM projects WHERE url NOT IN (SELECT url FROM files);")
    return [i[0] for i in cursor]
