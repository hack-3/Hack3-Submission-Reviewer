from typing import Set

import requests


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

    response = requests.get(url)
    if response.status_code != 200:
        return set()

    html = response.text
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

    if "https://" not in url and "http://" not in url:
        url = "https://" + url

    links: Set[str] = set()
    tag = '<a class="block-wrapper-link fade link-to-software" href="'  # Tag we're looking for
    page = 1

    for i in range(first_page, last_page + 1):
        has_projects = False

        project_url = url.strip("/") + f"/project-gallery?page={page}"
        response = requests.get(project_url)

        if response.status_code != 200:
            continue

        html = response.text

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
        response = requests.get(url + f"?page={page}")
        has_projects = False

        if response.status_code != 200:
            continue
        html = response.text

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

    if "https://" not in url and "http://" not in url:
        url = "https://" + url

    response = requests.get(url)

    if response.status_code != 200:
        return ""

    html: str = response.text

    # Parsing gets a little bit tricky, though all descriptions(I hope) start with the tag <h2> and ends in a </div>
    description: str = html[html.index("<h2>"):]
    description = description[:description.index("</div>")]

    tags = ["<h2>", "</h2>", "<p>", "</p>"]
    for tag in tags:
        description = description.replace(tag, "")

    return description


def get_links(url: str) -> Set[str]:
    """
    Gets the source links associated with a particular project from devpost.com
    You are meant to pipe data from get_projects() into this function
    :param url: url is a str associated with a project
    :return:
    """

    if "https://" not in url and "http://" not in url:
        url = "https://" + url
    response: requests.api = requests.get(url)

    if response.status_code != 200:
        return set()

    html: str = response.text
    if '<ul data-role="software-urls" class="no-bullet">' not in html:
        return set()

    html = html[html.index('<ul data-role="software-urls" class="no-bullet">'):]
    html = html[:html.index("</ul>")]

    tag = 'href='
    links: Set[str] = set()
    while tag in html:
        html = html[html.index(tag) + 6:]
        links.add(html[:html.index('"')])

    return links


if __name__ == "__main__":
    print("Hacklathons: ")
    print()
    print("Hack3 Projects: ")
    print(get_projects_hackathon("hack3.devpost.com/", max_links=10))
    print()
    print("New Projects: ")
    print(get_projects_new(last_page=1))
    print()
    print("Description: ")
    print(get_description('https://devpost.com/software/mask_pi_hack3'))
    print()
    print("Source Links: ")
    print(get_links("https://devpost.com/software/ar-grapher"))
    print(get_hackathons())
