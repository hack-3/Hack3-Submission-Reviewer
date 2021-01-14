from typing import List

import requests


def get_hackathons(category="sd") -> List[str]:
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
    if (response.status_code != 200):
        return []

    html = response.text
    tag = '<a class="clearfix" data-role="featured_challenge" href="'

    links: List[str] = []

    while tag in html:
        html = html[html.index(tag) + 57:]  # tag is 57 characters long
        links.append(html[:html.index('">')])  # "> is the ending part of the tag, so we are only getting the url

    return links


def get_projects(url) -> List[str]:
    """
    Gets all the projects associated with the hackathon from devpost.com.
    You are meant to pipe data from get_hackathons() into this function
    :param url: url is a str associated with a hackathon
    :return: List of project urls
    """

    if ("https://" not in url and "http://" not in url):
        url = "https://" + url

    links: List[str] = []
    page = 1

    while True:
        has_projects = False

        project_url = url.strip("/") + f"/project-gallery?page={page}"
        response = requests.get(project_url)

        if (response.status_code != 200):
            continue

        html = response.text
        tag = '<a class="block-wrapper-link fade link-to-software" href="'  # Tag we're looking for, right after this is the link

        while tag in html:
            html = html[html.index(tag) + 58:]  # tag is 58 characters long
            links.append(html[:html.index('">')])  # "> is the ending part of the tag, so we are only getting the url

            has_projects = True

        if not has_projects:  # Should only trigger if the while loop hasn't triggered yet, i.e. there is no projects
            break
        page += 1

    return links


def get_description(url) -> str:
    """
    Gets the description associated with a particular project from devpost.com
    You are meant to pipe data from get_projects() into this function
    :param url: url is a str associated with a project
    :return: Description of the project
    """

    if ("https://" not in url and "http://" not in url):
        url = "https://" + url

    response = requests.get(url)

    if (response.status_code != 200):
        return ""

    html: str = response.text

    # Parsing gets a little bit tricky, though all descriptions(I hope) start with the tag <h2> and ends in a </div>
    description: str = html[html.index("<h2>"):]
    description = description[:description.index("</div>")]

    tags = ["<h2>", "</h2>", "<p>", "</p>"]
    for tag in tags:
        description = description.replace(tag, "")

    return description


def get_links(url) -> List[str]:
    """
    Gets the source links associated with a particular project from devpost.com
    You are meant to pipe data from get_projects() into this function
    :param url: url is a str associated with a project
    :return:
    """

    if ("https://" not in url and "http://" not in url):
        url = "https://" + url
    response: requests.api = requests.get(url)

    if (response.status_code != 200):
        return []

    html: str = response.text
    html = html[html.index('<ul data-role="software-urls" class="no-bullet">'):]
    html = html[:html.index("</ul>")]

    tag = 'href='
    links: List[str] = []
    while (tag in html):
        html = html[html.index(tag) + 6:]
        links.append(html[:html.index('"')])

    return links


if (__name__ == "__main__"):
    print("Hacklathons: ")
    print(get_hackathons())
    print()
    print("Hack3 Projects: ")
    print(get_projects("hack3.devpost.com/"))
    print()
    print("Description: ")
    print(get_description('https://devpost.com/software/mask_pi_hack3'))
    print()
    print("Source Links: ")
    print(get_links("https://devpost.com/software/ar-grapher"))