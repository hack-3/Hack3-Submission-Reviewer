import threading
import time
from typing import List, Tuple
from core import mysql_functions, webscraping_functions, misc_functions


def monitor_site() -> None:
    """
    Sends a request every 30 seconds to the devpost site to monitor it for new projects.
    :return: None
    """
    while True:
        print("Request sent")
        store_projects_batch(ending_page=1, max_links=5)
        time.sleep(30)


def store_projects_batch(starting_page=1, ending_page=10, max_links=999999) -> None:
    """
    Grabs a batch of files and stores them into the `projects` table.
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
    Looks for github link in a devpost project and grabs most of the files to hash.
    This sores information in the `files` table.
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

        for github_url in github_urls:
            misc_functions.store_github_repo(cursor, github_url, url)
            connection.commit()

    connection.commit()

    cursor.close()
    connection.close()


def check_file(url: str) -> Tuple[List[str], List[Tuple[str]]]:
    """
    Checks a devpost url
    1) Any similar descriptions
    2) Any similar Files
    :param url: Devpost Project URL
    :return: Similar Descriptions, Similar Files [devpost url], [(githubUrl, devpostUrl, fileName, fileHash)]
    """
    if "devpost" not in url:
        print("Not a working url")
        return [], []

    connection = mysql_functions.get_connection()
    cursor = connection.cursor()

    desc = []
    desc_hash = misc_functions.get_description_hash(url)

    for dHash in mysql_functions.get_descriptions(cursor, url):
        if misc_functions.check_diff(desc_hash, dHash[1]):
            desc.append(dHash[0])

    file_ = []
    for file in misc_functions.get_devpost_github(url):
        user, repo, file_name, file_ext = misc_functions.parse_github_raw(file)
        f_hash = misc_functions.get_string_hash(webscraping_functions.get_html(file))

        for f in mysql_functions.get_files_by_ext(cursor, file_ext, url):
            if misc_functions.check_diff(f_hash, f[3]):
                file_.append(f)

    return desc, file_


def check_file_2(url: str) -> Tuple[List[str], List[Tuple[str]]]:
    """
    Same as check_file but multithreaded
    :param url: Devpost Project URL
    :return: Similar Descriptions, Similar Files [devpost url], [(githubUrl, devpostUrl, fileName, fileHash)]
    """
    if "devpost" not in url:
        print("Not a working url")
        return [], []

    connection = mysql_functions.get_connection()
    cursor = connection.cursor()

    desc = []
    desc_hash = misc_functions.get_description_hash(url)

    for dHash in mysql_functions.get_descriptions(cursor, url):

        if misc_functions.check_diff(desc_hash, dHash[1]):
            desc.append(dHash[0])

    file_ = []
    threads = []

    for file in misc_functions.get_devpost_github(url):
        user, repo, file_name, file_ext = misc_functions.parse_github_raw(file)
        f_hash = misc_functions.get_string_hash(webscraping_functions.get_html(file))

        t = threading.Thread(
            target=lambda: check_file_2_internal(file_, f_hash, mysql_functions.get_files_by_ext(cursor, file_ext, url)))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    cursor.close()
    connection.close()

    return desc, file_


def check_file_2_internal(files: List[Tuple[str]], file_hash: str, other_files: List[Tuple[str]]) -> None:
    """
    Internal method for the threads to run
    :param files: Main list of files, abusing mutability
    :param file_hash: File hash you're comparing to
    :param other_files: All files in need of comparing
    :return: None
    """
    for f in other_files:
        if misc_functions.check_diff(file_hash, f[3]):
            files.append(f)
