import re
import time
from typing import List, Tuple
from fuzzywuzzy import fuzz
import tlsh
from util import mysql_util, webscraping_utils


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
        return ratio > 80  # TODO - find good ratio here


def store_project(devpost_url: str):
    html = webscraping_utils.get_html(devpost_url)

    desc_hash = get_hash(webscraping_utils.get_project_description("", html=html))
    github_links = webscraping_utils.get_project_sources("", html=html)
    mysql_util.store_devpost_project(devpost_url, ",".join(github_links), desc_hash)

    store_source(devpost_url, github_links)


def store_projects_batch(starting_page: int = 1, ending_page: int = 10):
    if starting_page <= 0:
        starting_page = 1

    while starting_page <= ending_page:
        projects = webscraping_utils.get_new_projects(starting_page)

        for project in projects:
            store_project(project)

        starting_page += 1


def store_source(devpost_url, github_links):
    if mysql_util.is_project_added(devpost_url):
        print(f"Skipping project {devpost_url}")
        return

    print(f"Storing project {devpost_url}")

    for link in github_links:
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
            mysql_util.store_file(devpost_url, file_hash, name, ext)

    mysql_util.mark_project_checked(devpost_url)


def store_project_sources():
    unadded_projects = mysql_util.get_unadded_projects()

    for source in unadded_projects:
        store_source(source[0], source[1].split(","))


def check_project(devpost_url: str):
    duplicate = bool(re.search("-[a-z0-9]{6}$", devpost_url))
    if duplicate:
        print("Project might be duplicate")

    html = webscraping_utils.get_html(devpost_url)
    desc_hash = get_hash(webscraping_utils.get_project_description("", html=html))

    similar = {}

    print("Checking description")
    for entry in mysql_util.get_desc_hashes():
        if compare_hashes(desc_hash, entry[1]):
            print(f"Project is similar to {entry[0]}")

            similar.setdefault(entry[0], 0)
            similar[entry[0]] += 1
    sources = webscraping_utils.get_project_sources("", html=html)
    file_hashes = []
    for source in sources:
        user, repo = get_user_repo(source)

        for file in webscraping_utils.get_github_files(user, repo):
            print(f" - Hashing f{file[0]}")

            file_hashes.append((file[0], get_hash(webscraping_utils.get_file_content_raw(file[1]))))

    for h in file_hashes:
        print(f"Checking file {h[0]}")

        hashes = mysql_util.get_file_hashes(parse_file_name(h[0])[1])

        if hashes:
            for h2 in hashes:
                if compare_hashes(h[1], h2[2]):
                    print(f"File {h[0]} is similar to {h2[1]} from project {h2[0]}")

                    similar.setdefault(h2[0], 0)
                    similar[h2[0]] += 1

    output_log(devpost_url, duplicate, similar, len(file_hashes) + 1)


def output_log(devpost_url, possible_duplicate, similar, num_files):
    with open("output.txt", "w+") as f:
        f.write(f"Writing check for project {devpost_url}\n\n")

        if possible_duplicate:
            f.write("Project might be a duplicate - Search for projects with similar name\n\n")

        if not similar:
            f.write("Project is not similar to any in the dabase")
        else:
            for project in similar:
                f.write(
                    f"{project} has {similar[project]} similar files ({int(similar[project] / num_files * 100)}%)\n")


def monitor_site() -> None:
    """
    Sends a request every 30 seconds to the devpost site to monitor it for new projects.
    :return: None
    """
    while True:
        print("Request sent")
        store_projects_batch(ending_page=1)
        time.sleep(30)
