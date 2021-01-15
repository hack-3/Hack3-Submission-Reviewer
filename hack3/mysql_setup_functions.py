import mysql.connector


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


def create_url_table(user, password, host) -> None:
    """
    Creates a table called "project_url". It is used for store_urls().
    :param user: Username
    :param password: Password
    :param host: Host Ip
    :return: None
    """

    cnx = mysql.connector.connect(
        user=user, password=password,
        host=host,
        database="hack3"
    )

    curs = cnx.cursor()
    curs.execute("CREATE TABLE project_url (url VARCHAR(120));")

    cnx.commit()

    curs.close()
    cnx.close()
