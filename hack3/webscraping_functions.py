from typing import Set
from bs4 import BeautifulSoup
import requests
from hack3 import Config


def get_hackathons(category: str = "sd") -> Set[str]:
    """
    Gets the hackathons on devpost.com/hackathons front page.
    :param: Type is sd(Submission Deadline) or ra(Recently Added); default is sd
    :return: List of urls to different hackathons
    """

    if category == "sd":
        url = "https://devpost.com/hackathons?search=&challenge_type=all&sort_by=Submission+Deadline"
    else:  # Setting the default url to Recently Added
        url = "https://devpost.com/hackathons?search=&challenge_type=all&sort_by=Recently+Added"

    html = get_html(url)
    tag = '<a class="clearfix" data-role="featured_challenge" href="'

    links: Set[str] = set()

    while tag in html:
        html = html[html.index(tag) + 57:]  # tag is 57 characters long
        links.add(html[:html.index('">')])  # "> is the ending part of the tag, so we are only getting the url

    return links


def get_projects_hackathon(url: str, first_page: int = 1, last_page: int = 10000, max_links: int = 999999) -> Set[str]:
    """
    Gets all the projects from a hackathon
    You are meant to pipe data from get_hackathons() into this function
    :param url: url is a str associated with a hackathon
    :param first_page: First page you're looking for, inclusive
    :param last_page: Last page you're looking for, inclusive
    :param max_links: Number of links you're looking for
    :return: List of project urls
    """

    url = fix_url(url)

    links: Set[str] = set()
    tag = '<a class="block-wrapper-link fade link-to-software" href="'  # Tag we're looking for
    page = 1

    for i in range(first_page, last_page + 1):
        has_projects = False

        project_url = url.strip("/") + f"/project-gallery?page={page}"
        html = get_html(project_url)

        if html == "":
            continue

        while tag in html:
            html = html[html.index(tag) + 58:]  # tag is 58 characters long
            links.add(html[:html.index('">')])  # "> is the ending part of the tag, so we are only getting the url

            has_projects = True

            if len(links) >= max_links:
                return links

        if not has_projects:  # Should only trigger if the while loop hasn't triggered yet, i.e. there is no projects
            break
        page += 1

    return links


def get_projects_new(first_page: int = 1, last_page: int = 10000, max_links: int = 999999) -> Set[str]:
    """
    Gets the projects in devpost.com/software/newest
    :param max_links: maximum amount of links you want
    :param first_page: Starts at 1
    :param last_page: Ending page, will stop before if no more projects - inclusive
    :return: List of projects
    """
    url = "https://devpost.com/software/newest"
    tag = '<a class="block-wrapper-link fade link-to-software" href="'  # Tag we're looking for
    links: Set[str] = set()

    for page in range(first_page, last_page + 1):
        has_projects = False

        html = get_html(url + f"?page={page}")

        while tag in html:
            html = html[html.index(tag) + 58:]
            links.add(html[:html.index('">')])

            has_projects = True

            if len(links) >= max_links:
                return links

        if not has_projects:
            break

    return links


def get_description(url: str) -> str:
    """
    Gets the description associated with a particular project from devpost.com
    You are meant to pipe data from get_projects() into this function
    :param url: url is a str associated with a project
    :return: Description of the project
    """

    html = get_html(url)
    if html == "":
        return html
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()

    text = text[text.index("Updates") + 8:text.index("Built With")].strip()
    return text


def get_links(url: str) -> Set[str]:
    """
    Gets the source links associated with a particular project from devpost.com
    You are meant to pipe data from get_projects() into this function
    :param url: url is a str associated with a project
    :return:
    """

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

    config = Config.Config()

    files = set()
    trees = set()

    # Only has a recursion of 3 cause we don't neeeeed that many files, but we can increase it
    link = f"https://api.github.com/repos/{user}/{repo}/git/trees/master?recursive={recursive}"

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


def fix_url(url: str) -> str:
    """
    Internal method to "fix" an url if it doesn't have the required components
    :param url: Url you want to fix
    :return: Fixed url
    """

    if "https://" not in url and "http://" not in url:
        url = "https://" + url
    return url


def get_html(url: str) -> str:
    """
    Gets the html of a document
    :param url: Url of the webpage
    :return: Html of document
    """
    response = requests.get(fix_url(url))

    if response.status_code != 200:
        return ""
    return response.text
