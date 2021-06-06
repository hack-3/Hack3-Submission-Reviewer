import re
from typing import List
from fuzzywuzzy import fuzz
import tlsh
from util import mysql_datatypes as DataType, mysql_util, webscraping_utils


def get_hash(string: str) -> str:
    hash_ = tlsh.hash(string.encode("utf-8"))
    return hash_ if hash_ != "TNULL" else f"N{string}"


def parse_file_name(file_name: str) -> List[str]:
    temp = file_name.rsplit(".", 1)

    if len(temp) == 1:
        temp.insert(0, "")

    return temp


def compare_hashes(hash1: str, hash2: str) -> bool:
    if hash1[0] != hash2[0]:
        return False

    if hash1[0] == "T":
        diff = tlsh.diff(hash1, hash2)

        return diff < 100  # TODO - find good values here
    else:
        ratio = fuzz.ratio(hash1, hash2)
        return ratio > 70  # TODO - find good ratio here


def store_projects(starting_page: int = 1, ending_page: int = 10):
    if starting_page <= 0:
        starting_page = 1

    while starting_page <= ending_page:
        projects = webscraping_utils.get_new_projects(starting_page)

        for project in projects:
            print(f"Storing project {project}")

            html = webscraping_utils.get_html(project)

            desc_hash = get_hash(webscraping_utils.get_project_description("", html=html))
            github_links = ",".join(webscraping_utils.get_project_sources("", html=html))

            mysql_util.store_devpost_project(project, github_links, desc_hash)

        starting_page += 1


def store_project_sources():
    unadded_projects = mysql_util.get_values("projects", "devpostUrl", "githubSources", restrictions=["added = FALSE"])

    for source in unadded_projects:
        print(f"Storing project {source[0]}")
        links = source[1].split(",")

        for link in links:
            if link == "":
                continue

            user, repo = re.findall("^https://github.com/([\w-]+)/([\w-]+)", link)[0]
            file_links = webscraping_utils.get_github_files(user, repo)

            for file in file_links:
                file_hash = get_hash(webscraping_utils.get_file_content(file[1]))

                if file_hash == "":
                    return

                name, ext = parse_file_name(file[0])
                mysql_util.store_file(source[0], file_hash, name, ext)

        mysql_util.update_table("projects", restrictions=[f"devpostUrl='{source[0]}'"], added=DataType.Bool(True))
