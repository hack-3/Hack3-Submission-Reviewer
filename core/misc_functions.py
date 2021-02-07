from typing import List, Iterable
from fuzzywuzzy import fuzz
import tlsh
from core import config, mysql_functions, webscraping_functions


def get_string_hash(string: str) -> str:
    """
    Returns the hash of a string
    :param string: String you want hashed
    :return: Hashed String
    """
    h1 = tlsh.hash(string.encode("utf-8"))
    return h1 if h1 != "TNULL" else f"N{string}"


def get_description_hash(url: str) -> str:
    """
    Internal function to get the hash of the description of a particular file
    :param url: Project url
    :return: None
    """
    description = webscraping_functions.get_description(url)
    return get_string_hash(description)


def parse_file_name(file: str) -> List[str]:
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


def parse_github_raw(url: str) -> List[str]:
    """
    Parses a raw.githubusercontent.com url to get the user and repo
    :param url:
    :return: List[user, repo, file name, file extension]
    """
    args = url[url.index("github"):].split('/')

    user = args[1]
    repo = args[2]
    file = args[-1]
    file_body = parse_file_name(file)

    return [user, repo, file_body[0], file_body[1]]


def get_only_github(url: str) -> List[str]:
    """
    Gets only the github url from a devpost.com/software url
    :param url:
    :return:
    """

    urls = webscraping_functions.get_links(url)

    return [u for u in urls if "github" in u]


def get_devpost_github(url: str) -> Iterable[str]:
    """
    Generator that returns all the files in a devpost project.
    :param url:
    :return:
    """

    for u in get_only_github(url):
        args = u[u.index("github"):].split('/')

        for file in webscraping_functions.get_github_files(args[1], args[2]):
            yield file


def store_github_repo(curs, github_url: str, devpost_url: str = "") -> None:
    """
    Stores the files from a github repo
    :param github_url:
    :param devpost_url:
    :return:
    """

    if "github" not in github_url:
        return

    args = github_url[github_url.index("github"):].split('/')
    if len(args) < 3:
        print(github_url)
        return
    print("Github Repo:", args[1], args[2])

    file_urls = webscraping_functions.get_github_files(args[1], args[2])

    for url in file_urls:
        if "venv" in url or ".idea" in url or ".vscode" in url:
            continue

        user, repo, file_name, file_ext = parse_github_raw(url)

        if file_ext in config.disallowed_extensions:
            continue
        print(file_name, file_ext)

        file_body = webscraping_functions.get_html(url)
        hash_ = get_string_hash(file_body)
        github_repo = f"https://github.com/{user}/{repo}"

        mysql_functions.store_file(curs, github_repo, devpost_url, hash_, file_name, file_ext)


def check_diff(hash1: str, hash2: str) -> bool:
    """
    Checks the difference between 2 hashes
    :param hash1: One hash
    :param hash2: Another Hash
    :return: If hashes are similar
    """
    if hash1[0] == hash2[0] == "T":
        diff = tlsh.diff(hash1, hash2)

        if diff <= 102:
            return True
        else:
            return False

    elif hash1[0] == hash2[0] == "N":
        ratio = fuzz.ratio(hash1, hash2)

        if ratio >= 0.8:
            return True
        else:
            return False
    return False
