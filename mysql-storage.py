import mysql.connector

import webscraping_functions


def get_connection() -> mysql.connector:
    """
    Returns a connection to a server
    :return: mysql.connector
    """

    return mysql.connector.connect(
        user="root", password="password",
        host="127.0.0.1",
        database="hack3"
    )


def create_url_table():
    """
    Creates a table called "project_url". It is used for store_urls()
    :return: None
    """

    cnx = get_connection()
    cursor = cnx.cursor()
    cursor.execute("CREATE TABLE project_url (url VARCHAR(120));")

    cnx.commit()

    cursor.close()
    cnx.close()


def store_one_url(cursor: mysql.connector.cursor.MySQLCursor, link: str):
    """
    Stores a singular url into a database, but you may need to get rid of type annotations as I had to modify mysql's base connector to import it.
    :param cursor: Mysql cursor
    :param link: Link to a project
    :return: None
    """

    add_url = ("INSERT INTO project_url "
               "(url) "
               "VALUES (%(url)s)")
    cursor.execute(add_url, {"url": link})

def store_urls_batch(starting_page=1, ending_page=10, max_links=999999):
    """
    Stores the urls of recently created projects
    :param starting_page: starting page of projects you want to add(inclusive)
    :param ending_page: ending page you want to add(inclusive)
    :return: None
    """
    links = webscraping_functions.get_projects_new(starting_page, ending_page, max_links)


    cnx = get_connection()
    cursor = cnx.cursor()

    for link in links:
        store_one_url(cursor, link)

    cnx.commit()

    cursor.close()
    cnx.close()

# create_url_table()
store_urls_batch()