from typing import List, Tuple
import mysql.connector
from mysql.connector import cursor
from datetime import datetime
from core.Config_old import Config


def get_connection() -> mysql.connector:
    """
    Returns a connection to a server
    :return: mysql.connector
    """

    config = Config()

    return mysql.connector.connect(
        user=config.user, password=config.password,
        host=config.host,
        database="core"
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


def store_into_files(curs: cursor.MySQLCursor, githubUrl: str, devpostUrl: str, file_hash: str, file_name: str,
                     extension: str) -> None:
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
            f"INSERT IGNORE INTO files (githubUrl, devpostUrl, timeAdded, fileHash, fileName, extension) VALUES ('{githubUrl}', '{devpostUrl}', '{datetime.today()}', '{file_hash}', '{file_name}', '{extension}');")
    except Exception as e:
        print(e)


def get_unadded_urls(curs: cursor.MySQLCursor) -> List[str]:
    """
    Gets the urls from projects table that haven't been added to the files table
    :param curs: The cursor so we can open/close things outside of function
    :return: List of urls
    """
    curs.execute("SELECT url FROM projects WHERE url NOT IN (SELECT devpostUrl FROM files);")
    return [i[0] for i in curs]

def get_descriptions(curs: cursor.MySQLCursor, url: str) -> List[Tuple[str]]:
    """
    Used to get the description hashes from the mysql database
    :param curs: The cursor so we can open/close things outside of function
    :param url: Url of the function so we don't include it
    :return: List of (url, hash)
    """
    curs.execute(f"SELECT url, descHash FROM projects WHERE url != '{url}'")
    return [i for i in curs]

def get_files_by_ext(curs: cursor.MySQLCursor, devpostUrl: str, extension: str) -> List[Tuple[str]]:
    """
    Used to get the hashes of files by a file extension
    :param curs: The cursor so we can open/close things outside of function
    :param devpostUrl: Devpost url so we don't compare identical files
    :param extension: Extension of the file
    :return: Files matching a particular extension
    """
    curs.execute(f"SELECT githubUrl, devpostUrl, fileName, fileHash FROM files WHERE extension = '{extension}' AND devpostUrl != '{devpostUrl}'")
    return [i for i in curs]