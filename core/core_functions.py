import threading
from mysql.connector import cursor
import time
from typing import List, Tuple
from core import mysql_functions, webscraping_functions, misc_functions


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
    links = webscraping_functions.get_project_in_new(starting_page, ending_page, max_links)

    connection = mysql_functions.get_connection()
    cursor = connection.cursor()

    for url in links:
        desc_hash = misc_functions.get_description_hash(url)

        mysql_functions.store_project(cursor, url, desc_hash)

    connection.commit()

    cursor.close()
    connection.close()


def store_files() -> None:
    """
    Stores and Hashes all of the files taken from github
    :return: None
    """
    connection = mysql_functions.get_connection()
    cursor = connection.cursor()

    devpost_urls = mysql_functions.get_unadded_urls(cursor)
    cursor.close()

    cursor = connection.cursor()

    for url in devpost_urls:
        print(url)

        github_urls = misc_functions.get_only_github(url)

        # print(url)
        # print(github_urls)

        for github_url in github_urls:
            misc_functions.store_github_repo(cursor, github_url, url)
            connection.commit()

    connection.commit()

    cursor.close()
    connection.close()


def check_file(url: str) -> Tuple[List[str], List[Tuple[str]]]:
    """
    Checks a devpost url
    :param url:
    :return:
    """
    if "devpost" not in url:
        print("Not a working url")
        return ([], [])

    connection = mysql_functions.get_connection()
    cursor = connection.cursor()

    desc = []
    descHash = misc_functions.get_description_hash(url)

    for dHash in mysql_functions.get_descriptions(cursor, url):
        if misc_functions.check_diff(descHash, dHash[1]):
            desc.append(dHash[0])

    file_ = []
    for file in misc_functions.get_devpost_github(url):
        user, repo, file_name, file_ext = misc_functions.parse_github_raw(file)
        fHash = misc_functions.get_string_hash(webscraping_functions.get_html(file))

        for f in mysql_functions.get_files_by_ext(cursor, file_ext, url):
            if misc_functions.check_diff(fHash, f[3]):
                file_.append(f)

    return desc, file_


def check_file_2(url: str) -> Tuple[List[str], List[Tuple[str]]]:
    """
    Does some stuff
    :param url:
    :return:
    """
    if "devpost" not in url:
        print("Not a working url")
        return ([], [])

    connection = mysql_functions.get_connection()
    cursor = connection.cursor()

    desc = []
    descHash = misc_functions.get_description_hash(url)

    for dHash in mysql_functions.get_descriptions(cursor, url):

        if misc_functions.check_diff(descHash, dHash[1]):
            desc.append(dHash[0])

    file_ = []
    threads = []

    for file in misc_functions.get_devpost_github(url):
        user, repo, file_name, file_ext = misc_functions.parse_github_raw(file)
        fHash = misc_functions.get_string_hash(webscraping_functions.get_html(file))

        t = threading.Thread(
            target=lambda: check_file_2_internal(file_, fHash, mysql_functions.get_files_by_ext(cursor, file_ext, url)))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

        # for f in mysql_functions.get_files_ext_table(cursor, file_ext, url):
        #     if misc_functions.check_diff(fHash, f[3]):
        #         file_.append(f)

    cursor.close()
    connection.close()

    return desc, file_


def check_file_2_internal(files: List[Tuple[str]], fileHash: str, otherFiles: List[Tuple[str]]):
    for f in otherFiles:
        if misc_functions.check_diff(fileHash, f[3]):
            files.append(f)
