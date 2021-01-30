from typing import List
from fuzzywuzzy import fuzz
from core import mysql_functions_old
from core import webscraping_functions_old
from core import Config_old
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
    links = webscraping_functions_old.get_projects_new(starting_page, ending_page, max_links)

    connection = mysql_functions_old.get_connection()
    cursor = connection.cursor()

    for url in links:
        desc_hash = get_description_hash(url)

        mysql_functions_old.store_into_projects(cursor, url, desc_hash)

    connection.commit()

    cursor.close()
    connection.close()


def get_description_hash(url: str) -> str:
    """
    Internal function to get the hash of the description of a particular file
    :param url: Project url
    :return: None
    """
    description = webscraping_functions_old.get_description(url)
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
    connection = mysql_functions_old.get_connection()
    cursor = connection.cursor()

    devpost_links = mysql_functions_old.get_unadded_urls(cursor)
    cursor.close()

    cursor = connection.cursor()

    for link in devpost_links:
        sources = webscraping_functions_old.get_links(link)

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
    config = Config_old.Config()

    if "github" in github_url:
        args = github_url[github_url.index("github"):].split('/')
        if len(args) < 3:
            print(github_url)
            return

        files = webscraping_functions_old.get_github_files(args[1], args[2])

        print(args[1], args[2])

        for link in files:
            if "venv" in link or ".idea" in link:
                continue

            args = link[link.index("github"):].split('/')

            user = args[1]
            repo = args[2]
            file = args[-1]
            file_body = get_file_info(file)

            if file_body[1] in config.disallowed_extensions:
                continue

            html = webscraping_functions_old.get_html(link)
            h1 = get_string_hash(html)

            github_repo = f"https://github.com/{user}/{repo}"

            mysql_functions_old.store_into_files(curs, github_repo, devpost_url, h1, file_body[0], file_body[1])


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


def check_project(url: str):
    """
    Checks a particular project from a devpost site
    :param url: devpost.com/software/something
    :return: None
    """
    description = webscraping_functions_old.get_description(url)
    links = webscraping_functions_old.get_links(url)

    desc_hash = tlsh.hash(description.encode("utf-8"))
    files = set()

    for link in links:
        if "github" in link:
            args = link[link.index("github"):].split('/')
            if len(args) < 3:
                print(link)
                return

            files = webscraping_functions_old.get_github_files(args[1], args[2])

            print(args[1], args[2])

            files.update(webscraping_functions_old.get_github_files(args[1], args[2]))

    connection = mysql_functions_old.get_connection()
    curs = connection.cursor()

    if desc_hash == "TNULL":
        desc_hash = "N" + description
        print(f"{url}'s description is too short to be hashed!")

    d = mysql_functions_old.get_descriptions(curs, url)
    for i in d:
        other_hash = i[1]

        if other_hash[0] == desc_hash[0] == "T":
            diff = tlsh.diff(other_hash, desc_hash)
            if diff <= 50:  # change var to whatever you want
                print(f"File description seems to match with {i[0]} with diff {diff}")

        elif other_hash[0] == desc_hash[0] == "N":
            ratio = fuzz.ratio(other_hash, desc_hash)

            if ratio >= 0.8:
                print(f"File description seems to match with {i[0]} similarity {ratio}")

    config = Config_old.Config()

    for f in files:
        html = webscraping_functions_old.get_html(f)
        file_hash = get_string_hash(html)

        args = f[f.index("git"):].split('/')

        user = args[1]
        repo = args[2]
        file = args[-1]
        file_body = get_file_info(file)

        if file_body[1] in config.disallowed_extensions:
            continue

        link = f"https://github.com/{user}/{repo}"

        if file_hash == 'TNULL':
            file_hash = "N" + html

        for i in mysql_functions_old.get_files_by_ext(curs, url, file_body[1]):
            if i[0] == link:
                print(f"Project is using the same github as another: {i[3]} Devpost: {i[1]}")

            if i[3] == desc_hash[0] == "T":
                diff = tlsh.diff(i[3], desc_hash)
                if diff <= 50:  # change var to whatever you want
                    print(f"File seems to match with {i[2]} with diff {diff} from {i[0]} from {i[1]}")

            elif i[3] == desc_hash[0] == "N":
                ratio = fuzz.ratio(i[3], desc_hash)

                if ratio >= 0.8:
                    print(f"File description seems to match with {i[2]} similarity {ratio} from {i[0]} from {i[1]}")