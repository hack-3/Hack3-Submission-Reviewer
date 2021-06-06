import re
from typing import List, Tuple
from fuzzywuzzy import fuzz
import tlsh
from util import mysql_datatypes as DataType, mysql_util, webscraping_utils


def get_hash(string: str) -> str:
    hash_ = tlsh.hash(string.encode("utf-8"))
    return hash_ if hash_ != "TNULL" else f"N{string}"


def parse_file_name(file_name: str) -> List[str]:
    file = re.search("(?:\.+/)?([^/]+)$", file_name)
    if not file:
        print(f"{file_name} has a problem")
        return ["_", "_"]

    temp = file.group().rsplit(".", 1)

    if len(temp) == 1:
        temp.insert(0 if "." in file_name else 1, "_")

    return temp


def get_user_repo(github_link: str) -> Tuple[str, str]:
    return re.findall("^https://github.com/([\w-]+)/([\w-]+)", github_link)[0]


def compare_hashes(hash1: str, hash2: str) -> bool:
    if hash1[0] != hash2[0]:
        return False

    if hash1[0] == "T":
        diff = tlsh.diff(hash1, hash2)

        return diff < 100  # TODO - find good values here
    else:
        ratio = fuzz.ratio(hash1, hash2)
        return ratio > 70  # TODO - find good ratio here


def store_project(devpost_url: str):
    html = webscraping_utils.get_html(devpost_url)

    desc_hash = get_hash(webscraping_utils.get_project_description("", html=html))
    github_links = ",".join(webscraping_utils.get_project_sources("", html=html))

    mysql_util.store_devpost_project(devpost_url, github_links, desc_hash)


def store_projects_batch(starting_page: int = 1, ending_page: int = 10):
    if starting_page <= 0:
        starting_page = 1

    while starting_page <= ending_page:
        projects = webscraping_utils.get_new_projects(starting_page)

        for project in projects:
            print(f"Storing project {project}")

            store_project(project)

        starting_page += 1


def store_project_sources():
    unadded_projects = mysql_util.get_unadded_projects()

    for source in unadded_projects:
        print(f"Storing project {source[0]}")
        links = source[1].split(",")

        for link in links:
            if link == "":
                continue

            user, repo = get_user_repo(link)
            file_links = webscraping_utils.get_github_files(user, repo)

            for file in file_links:
                print(f" - Storing file {file[0]}")

                file_hash = get_hash(webscraping_utils.get_file_content_raw(file[1]))

                if file_hash == "":
                    return

                name, ext = parse_file_name(file[0])
                mysql_util.store_file(source[0], file_hash, name, ext)

        mysql_util.mark_project_checked(source[0])


def check_project(devpost_url: str):
    if re.search("-[a-z][a-z][a-z][a-z][a-z][a-z]$", devpost_url):
        print("Project might be duplicate")

    html = webscraping_utils.get_html(devpost_url)
    desc_hash = get_hash(webscraping_utils.get_project_description("", html=html))

    for entry in mysql_util.get_desc_hashes():
        if compare_hashes(desc_hash, entry[1]):
            print(f"Project is similar to {entry[0]}")

    sources = webscraping_utils.get_project_sources("", html=html)
    file_hashes = []
    for source in sources:
        user, repo = get_user_repo(source)

        for file in webscraping_utils.get_github_files(user, repo):
            file_hashes.append((file[0], get_hash(webscraping_utils.get_file_content_raw(file[1]))))

    for h in file_hashes:
        hashes = mysql_util.get_file_hashes(parse_file_name(h[0])[1])

        if hashes:
            for h2 in hashes:
                if compare_hashes(h[1], h2[2]):
                    print(f"File {h[0]} is similar to {h2[1]} from project {h2[0]}")
