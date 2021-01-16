import mysql.connector
from datetime import datetime
from hack3.Config import Config
from mysql.connector import cursor
from hack3 import webscraping_functions

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


def store_one_url(curs: cursor.MySQLCursor, link: str) -> None:
    """
    Stores a singular url into a database.
    :param curs: Mysql cursor
    :param link: Link to a project
    :return: None
    """

    if len(link) <= 120:
        curs.execute(f"INSERT IGNORE INTO project_url (url, time) VALUES ('{link}', '{datetime.today()}')")
    else:
        print(f"Link is too long for the database: {link}")


def store_urls_batch(starting_page=1, ending_page=10, max_links=999999):
    """
    Stores the urls of recently created projects, it is only meant to be run once on table creation to populate it.
    :param max_links: maximum amount of links you want
    :param starting_page: starting page of projects you want to add(inclusive), default is 1
    :param ending_page: ending page you want to add(inclusive), default is 10
    :return: None
    """
    links = webscraping_functions.get_projects_new(starting_page, ending_page, max_links)

    cnx = get_connection()
    curs = cnx.cursor()

    for link in links:
        store_one_url(curs, link)

    cnx.commit()

    curs.close()
    cnx.close()
