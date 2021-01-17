import mysql.connector
from hack3.Config import Config
from mysql.connector import errors


def create_database(user, password, host) -> None:
    """
    Creates the main database for this project
    :param user: Username
    :param password: Password
    :param host: Host Ip
    :return: None
    """

    cnx = mysql.connector.connect(
        user=user, password=password,
        host=host,
    )

    curs = cnx.cursor()
    curs.execute("CREATE DATABASE hack3")
    cnx.commit()

    curs.close()
    cnx.close()


def execute_query(user, password, host, query) -> None:
    """
    Executes a query, mostly for creating tables
    :param user: Username
    :param password: Password
    :param host: Host Ip
    :param query: Query you want to execute
    :return: None
    """
    cnx = mysql.connector.connect(
        user=user, password=password,
        host=host,
        database="hack3"
    )

    curs = cnx.cursor()
    curs.execute(query)
    cnx.commit()

    curs.close()
    cnx.close()
