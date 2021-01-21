from typing import List

from hack3 import mysql_functions
from hack3 import webscraping_functions
from hack3 import Config
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
    return get_string_hash(description)


def get_string_hash(string: str) -> str:
    """
    Returns the hash of a string
    :param string: String you want hashed
    :return: Hashed String
    """
    h1 = tlsh.hash(string.encode("utf-8"))
    return h1 if h1 != "TNULL" else f"N{string}"


def store_files() -> None:
    """
    Stores and Hashes all of the files taken from github
    :return: None
    """
    connection = mysql_functions.get_connection()
    cursor = connection.cursor()

    devpost_links = mysql_functions.get_unadded_urls(cursor)
    cursor.close()

    cursor = connection.cursor()

    for link in devpost_links:
        sources = webscraping_functions.get_links(link)

        for source in sources:
            if source.startswith("https://github.com"):
                store_github(cursor, source, link)
                connection.commit()

    connection.commit()

    cursor.close()
    connection.close()


def store_github(curs, github_url: str, devpost_url: str) -> None:
    """
    Stores all(not really) of the files associated with the github url
    :param curs: Cursor
    :param github_url: Url of github repo
    :param devpost_url: Url of devpost
    :return: None
    """
    config = Config.Config()

    if "github" in github_url:
        args = github_url[github_url.index("github"):].split('/')
        if len(args) < 3:
            print(github_url)
            return

        files = webscraping_functions.get_github_files(args[1], args[2])

        print(args[1], args[2])

        for link in files:
            if "venv" in link or ".idea" in link:
                continue

            args = link[link.index("github"):].split('/')

            user = args[1]
            repo = args[2]
            file = args[-1]
            file_body = get_file_info(file)

            print(file_body)

            if file_body[1] in config.disallowed_extensions:
                continue

            html = webscraping_functions.get_html(link)
            h1 = get_string_hash(html)

            github_repo = f"https://github.com/{user}/{repo}"

            mysql_functions.store_into_files(curs, github_repo, devpost_url, h1, file_body[0], file_body[1])


def get_file_info(file: str) -> List[str]:
    """
    Gets the file info, extension + name
    :param file: File
    :return: List[file name, file extension]
    """
    file = file.split(".")
    if len(file) == 1:
        file.append("")
    if len(file) > 2:
        extension = file.pop()
        file = ['.'.join(file), extension]

    return file
