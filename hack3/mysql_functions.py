from typing import List
import tlsh
import mysql.connector
from datetime import datetime
from hack3.Config import Config
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


def store_one_url(link: str) -> None:
    """
    Stores a singular url into a database.
    :param curs: Mysql cursor
    :param link: Link to a project
    :return: None
    """

    connection = get_connection()
    curs = connection.cursor()

    if len(link) <= 120:
        curs.execute(f"INSERT IGNORE INTO project_url (url, time) VALUES ('{link}', '{datetime.today()}')")
    else:
        print(f"Link is too long for the database: {link}")

    connection.commit()

    curs.close()
    connection.close()


def store_urls_batch(starting_page=1, ending_page=10, max_links=999999):
    """
    Stores the urls of recently created projects, it is only meant to be run once on table creation to populate it.
    :param max_links: maximum amount of links you want
    :param starting_page: starting page of projects you want to add(inclusive), default is 1
    :param ending_page: ending page you want to add(inclusive), default is 10
    :return: None
    """
    links = webscraping_functions.get_projects_new(starting_page, ending_page, max_links)

    for link in links:
        store_one_url(link)


def hash_descriptions():
    query = "SELECT url FROM project_url WHERE url NOT IN (SELECT url FROM project_description)"

    connection = get_connection()
    curs = connection.cursor()

    curs.execute(query)
    urls = [i[0] for i in curs]

    for link in urls:
        description = webscraping_functions.get_description(link)
        h1 = tlsh.hash(description.encode('utf-8'))

        curs.execute(
            f"INSERT INTO project_description (url, time, descHash) VALUES ('{link}', '{datetime.today()}', '{h1 if h1 != 'TNULL' else f'N{description}'}')")

    connection.commit()

    curs.close()
    connection.close()
