from hack3 import mysql_functions
from hack3 import webscraping_functions
import time
import tlsh


def monitor_site() -> None:
    """
    Monitors the devpost site to look for recently created projects
    :return: None
    """
    while True:
        print("Request sent")
        store_projects_batch(ending_page=1, max_links=5)
        time.sleep(30)


def store_projects_batch(starting_page=1, ending_page=10, max_links=999999) -> None:
    """
    Stores projects in batches 
    :param starting_page: Starting page you want to use
    :param ending_page: Ending page you want to use
    :param max_links: Maximum amount of links you want to gather
    :return: None
    """
    links = webscraping_functions.get_projects_new(starting_page, ending_page, max_links)

    connection = mysql_functions.get_connection()
    cursor = connection.cursor()

    for url in links:
        desc_hash = get_description_hash(url)

        mysql_functions.store_into_projects(cursor, url, desc_hash)

    connection.commit()

    cursor.close()
    connection.close()


def get_description_hash(url: str) -> str:
    """
    Internal function to get the hash of the description of a particular file
    :param url: Project url
    :return: None
    """
    description = webscraping_functions.get_description(url)
    h1 = tlsh.hash(description.encode("utf-8"))

    return h1 if h1 != "TNULL" else f"N{description}"


def store_files() -> None:
    """
    Stores and Hashes all of the files taken from github
    :return: None
    """
