from typing import Set
from bs4 import BeautifulSoup
import requests
from core import config


def set_url_type(url: str) -> str:
    """
    This is a method to set the url type. If the url doesn't contains a start (http:// or https://), then a https:// is added
    :param url: Url that might or might not have a type(http/https_
    :return: Url with a type added
    """

    if "https://" not in url and "http://" not in url:
        url = "https://" + url
    return url


def get_html(url: str) -> str:
    """
    This is a method to scrape the html of a document provided a link to a website.
    :param url: Url of the webpage that you want to scrape.
    :return: String containing html of document.
    """
    response = requests.get(set_url_type(url))

    if response.status_code != 200:
        return ""
    return response.text


def get_description(url: str) -> str:
    """
    This gets the description of a devpost project.
    :param url: The url of a devpost project that you want to get the description of.
    :return: The description of the project
    """

    if "devpost.com/software" not in url:
        print("This is not a devpost project!")
        return ""

    html = get_html(url)
    if html == "":
        return html

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()

    text = text[text.index("Updates") + 8:text.index("Built With")].strip()
    return text


def get_links(url: str) -> Set[str]:
    """
    This gets the urls of a devpost project, mostly to scan to see if the project has a github file.
    :param url: Url of a devpost project
    :return: Set of urls at bottom of devpost project.
    """

    if "devpost.com/software" not in url:
        print("This is not a devpost project!")
        return set()

    links: Set[str] = set()

    html = get_html(url)

    if '<ul data-role="software-urls" class="no-bullet">' not in html:
        return set()

    html = html[html.index('<ul data-role="software-urls" class="no-bullet">'):]
    html = html[:html.index("</ul>")]

    tag = 'href='

    while tag in html:
        html = html[html.index(tag) + 6:]
        links.add(html[:html.index('"')])

    return links


def get_github_files(user: str, repo: str, recursive: int = 3) -> Set[str]:
    """
    Returns a set of links to the dl or parsing of raw files
    :param user: Owner of the repo
    :param repo: Repo
    :param recursive: Extra customizability for github api requests
    :return: Set of file links
    """

    files = set()
    trees = set()

    branches = f"https://api.github.com/repos/{user}/{repo}/branches"
    r1 = requests.get(branches, headers={"Authorization": f"token {config.github}"})

    branch = "master"
    if r1.status_code == 200:
        branch = r1.json()[0]["name"]

    # Only has a recursion of 3 cause we don't neeeeed that many files, but we can increase it
    link = f"https://api.github.com/repos/{user}/{repo}/git/trees/{branch}?recursive={recursive}"
    response = requests.get(link, headers={"Authorization": f"token {config.github}"})

    if response.status_code != 200:
        return files

    data = response.json()

    if "message" in data and data["message"] == "Not Found":
        return files

    for leaf in data["tree"]:
        type_ = leaf["type"]
        path = leaf["path"]

        if type_ == "tree":
            trees.add(path)
        elif type_ == "blob":
            files.add(f"https://raw.githubusercontent.com/{user}/{repo}/master/{path.replace(' ', '%20')}")
        else:
            print(type_)

    return files


def get_project_in_new(starting_page: int = 1, ending_page: int = 999999, max_urls: int = 999999) -> Set[str]:
    """
    This function scrapes all the functions from https//devpost.com/software/newest.
    It looks for "<a class="block-wrapper-link fade link-to-software" href=" within the html and pipes it into a set
    :param starting_page: The starting page that the webscraper starts on. Lowest page is 1.
    :param ending_page: The ending page that the webscraper ends on. This is NOT inclusive.
    :param max_urls: The maximum amount of urls that you want.
    :return: A set of all the scraped urls.
    """

    if starting_page < 1:
        starting_page = 1

    url = "https://devpost.com/software/newest"
    tag = '<a class="block-wrapper-link fade link-to-software" href="'  # Tag we're looking for
    links: Set[str] = set()

    for page in range(starting_page, ending_page):
        has_projects = False

        html = get_html(url + f"?page={page}")

        while tag in html:
            html = html[html.index(tag) + 58:]
            links.add(html[:html.index('">')])

            has_projects = True

            if len(links) >= max_urls:
                return links

        if not has_projects:
            break

    return links