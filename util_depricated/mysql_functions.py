from typing import List, Tuple
import mysql.connector
from mysql.connector import cursor, errors
from datetime import datetime
from util import config
import util.mysql_datatypes as DataType


def get_connection() -> mysql.connector:
    """
    Internal method to get a connection to the mysql server using the information from config.py
    :return: mysql.connector
    """

    return mysql.connector.connect(
        user=config.user, password=config.password,
        host=config.host,
        database="hack3"
    )


def insert_values(curs: cursor.MySQLCursor, table: str, **kwargs) -> None:
    """
    Basic function to store some data into a database
    :param curs: The mysql cursor
    :param table: Table to store data in
    :param kwargs: List of arguments and their values
    """
    params = ", ".join(map(lambda x: f"'{x}'", kwargs.keys()))
    values = ", ".join(map(lambda x: f"'{x}'", kwargs.keys()))

    try:
        curs.execute(
            f"INSERT IGNORE INTO {table} ({params}) VALUES ({values});")
    except Exception as e:
        print(e)


def create_table(curs: cursor.MySQLCursor, table_name: str, override=False, **kwargs: DataType):
    """
    Creates a mysql table
    """
    categories = ", ".join(map(lambda x: f"{x} {str(kwargs[x])}", kwargs))

    try:
        curs.execute(
            f"CREATE TABLE f{table_name} {'' if override else 'IF NOT EXISTS '}({categories})")
    except Exception as e:
        print(e)


def store_project(curs: cursor.MySQLCursor, url: str, desc_hash: str) -> None:
    """
    Stores a url with its hash in to `projects` table.
    :param curs: The cursor so we can open/close things outside of function
    :param url: Devpost URL
    :param desc_hash: Hash of the description
    :return: None
    """
    insert_values(curs, "projects", url=url, timeAdded=datetime.today(), descHash=desc_hash)

def get_values(curs: cursor.MySQLCursor, table: str, *categories: str, restrictions: list=None):
    if not restrictions:
        restrictions = []

    temp1 = ", ".join(categories)
    temp2 = "WHERE" if restrictions else "" + " AND ".join(restrictions)

    try:
        curs.execute(
            f"SELECT {temp1} FROM {table} {temp2}")
        return curs.fetchall()
    except errors.ProgrammingError as e:
        print(e)
        return []


def store_file(curs: cursor.MySQLCursor, github_url: str, devpost_url: str, file_hash: str, file_name: str,
               extension: str) -> None:
    """
    Stores a file into the `files` table
    :param curs: The cursor so we can open/close things outside of function
    :param github_url: Github Project Url
    :param devpost_url: Devpost Project URL
    :param file_hash: Hash of the file
    :param file_name: Name of the file
    :param extension: Extension of the file
    :return: None
    """
    insert_values(curs, "files", githubUrl=github_url, timeAdded=datetime.today(), devpostUrl=devpost_url,
                  fileHash=file_hash, fileName=file_name, extension=extension)


def store_file_ext(curs: cursor.MySQLCursor, github_url: str, devpost_url: str, file_hash: str, file_name: str,
                   extension: str) -> None:
    create_table(curs, extension, githubUrl=DataType.VarChar(120, True), devpostUrl=DataType.VarChar(120, True),
                 timeAdded=DataType.DateTime, fileHash=DataType.VarChar(100, True), fileName=DataType.VarChar(30))
    insert_values(curs, extension, githubUr=github_url, devpostUrl=devpost_url, timeAdded=datetime.today(),
                  fileHash=file_hash, fileName=file_name)


def get_unadded_urls(curs: cursor.MySQLCursor) -> List[str]:
    """
    Return all urls that haven't been added to the `projects` table
    Projects table is a collection of all the projects.
    :param curs: The cursor so we can open/close things outside of function
    :return: List of urls [url]
    """
    curs.execute("SELECT url FROM projects WHERE url NOT IN (SELECT devpostUrl FROM files);")
    return [i[0] for i in curs]


def get_descriptions(curs: cursor.MySQLCursor, url: str) -> List[Tuple[str]]:
    """
    Returns url, description hash from the `projects` table
    :param curs: The cursor so we can open/close things outside of function
    :param url: URL of a project
    :return: List of url, description [(url, description hash)]
    """
    curs.execute(f"SELECT url, descHash FROM projects WHERE url != '{url}'")
    return [i for i in curs]


def get_files_by_ext(curs: cursor.MySQLCursor, extension: str, devpost_url: str = "") -> List[Tuple[str]]:
    """
    Returns all files matching the extension which don't come from the same devpost project.
    :param curs: The cursor so we can open/close things outside of function
    :param devpost_url: URL of a project
    :param extension: Extension of the file
    :return: List of information of the file [(githubUrl, devpostUrl, fileName, fileHash)]
    """
    curs.execute(
        f"SELECT githubUrl, devpostUrl, fileName, fileHash FROM files WHERE extension = '{extension}' AND devpostUrl != '{devpost_url}'")
    return curs.fetchall()


def get_files_ext_table(curs: cursor.MySQLCursor, extension: str, devpost_url: str = "") -> List[Tuple[str]]:
    """
    Returns all files from a table of an extension.
    :param curs: The cursor so we can open/close things outside of function
    :param devpost_url: Devpost url so we don't compare identical files
    :param extension: Extension of the file
    :return: List of information of the file [(githubUrl, devpostUrl, fileName, fileHash)]
    """

    try:
        curs.execute(
            f"SELECT githubUrl, devpostUrl, fileName, fileHash FROM {extension} WHERE devpostUrl != '{devpost_url}'")
        return curs.fetchall()
    except errors.ProgrammingError:
        return []
