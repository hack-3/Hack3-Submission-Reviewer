import re
from typing import List, Tuple
import base64
import bs4
import requests
from util import configuration as c


def validate_url(url: str) -> bool:
    return bool(re.match(r"http(?:s)?://.+\..+", url))


def locate_urls(text: str) -> List[str]:
    return re.findall("(http(?:s)?://(?:www\.)?\w+\.\w+(?:[\w/\-]+)?)", text)


def get_html(url: str) -> str:
    if not validate_url(url):
        print(f"{url} does not match specified requirements")
        return ""

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
    }

    resp = requests.get(url, headers=headers)

    if not str(resp.status_code).startswith("2"):
        print(f"Request to {url} returned with staus code {resp.status_code}")
        print(resp.text)
        return ""

    return resp.text


def get_new_projects(page_number: int) -> List[str]:
    devpost = f"https://devpost.com/software/newest?page={page_number}"
    html = get_html(devpost)

    return re.findall("href=\"(https://devpost.com/software/[\w-]+)\"", html)


def get_hackathon_projects(hackathon_url: str, max_projects: int = 100) -> List[str]:
    projects = []
    page_number = 1
    hackathon_url = hackathon_url + "/project-gallery?page={}"

    while len(projects) < max_projects:
        html = get_html(hackathon_url.format(page_number))
        temp = re.findall("href=\"(https://devpost.com/software/[\w-]+)\"", html)

        if len(temp) == 0:
            break
        else:
            projects.extend(re.findall("href=\"(https://devpost.com/software/[\w-]+)\"", html))

    return projects


def get_project_sources(project_url: str, html: str = "") -> List[str]:
    if not html:
        html = get_html(project_url)

    parser = bs4.BeautifulSoup(html, features="html.parser")
    links = str(parser.find("nav", {"class": "app-links"}))

    return re.findall("href=\"(https://github\.com/[^/]+/[^\"]+)\"", links)


def get_project_description(project_url: str, html: str = "") -> str:
    if not html:
        html = get_html(project_url)

    parser = bs4.BeautifulSoup(html, features="html.parser")
    description = parser.find("div", {"id": "app-details-left"}).text

    return re.sub("\n+", "\n", re.sub('<[^<]+?>', '', description)).strip()


def explore_github_tree_api(tree_url: str) -> List[Tuple[str, str]]:
    files = []
    trees = []

    resp = requests.get(tree_url, headers={"Authorization": f"token {c.get_github_token()}"})

    if resp.status_code != 200:
        return []

    data = resp.json()
    for leaf in data["tree"]:
        type_ = leaf["type"]
        path = leaf["path"]
        url = leaf["url"]

        if type_ == "tree":
            trees.append(path)
        elif type_ == "blob":
            size = leaf["size"]  # Size is in bytes
            if size < 3000000:  # 3 MB
                # TODO - Make so this returns a raw.github, not api.github

                files.append((path, url))
            # else:
            #     print(f"{url} is too large")
        else:
            print(type_)

    if len(files) == 0:
        for i in trees:
            files.extend(explore_github_tree_api(i))

    return files


def explore_github_tree_raw(tree_url: str) -> List[Tuple[str, str]]:
    files = []
    trees = []

    resp = requests.get(tree_url, headers={"Authorization": f"token {c.get_github_token()}"})

    user, repo, branch = re.findall("^https://api.github.com/repos/([\w-]+)/([\w-]+)/git/trees/([\w+]+)", tree_url)[0]

    if resp.status_code != 200:
        return []

    data = resp.json()
    for leaf in data["tree"]:
        type_ = leaf["type"]
        path = leaf["path"]

        if re.search(r"(^|/)(env|node_modules|lib|static|docs)/", path):
            continue

        if type_ == "tree":
            trees.append(path)
        elif type_ == "blob":
            size = leaf["size"]  # Size is in bytes
            if size < 2000000:  # 2 MB
                files.append(
                    (path, f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path.replace(' ', '%20')}"))
            # else:
            #     print(f"{url} is too large")
        else:
            print(type_)

    if len(files) == 0:
        for i in trees:
            files.extend(explore_github_tree_raw(i))

    return files


def get_github_files(user: str, repo: str) -> List[Tuple[str, str]]:
    branches_url = f"https://api.github.com/repos/{user}/{repo}/branches"
    resp = requests.get(branches_url, headers={"Authorization": f"token {c.get_github_token()}"})

    branch = "main"
    if resp.status_code == 200:
        branches = [i["name"] for i in resp.json()]

        if "master" in branches:
            branch = "master"
        elif "main" in branches:
            branch = "main"
        else:
            branch = branches[0]

    link = f"https://api.github.com/repos/{user}/{repo}/git/trees/{branch}?recursive=3"  # Can change how far you want to look through
    return explore_github_tree_raw(link)


def get_file_content_api(file_link: str) -> str:
    resp = requests.get(file_link)
    if resp.status_code != 200:
        print(f"{file_link} returned with status code {resp.status_code}")
        return ""

    content = resp.json()["content"]
    return base64.decodebytes(content.encode("utf-8", errors="replace")).decode("utf-8", errors="replace")


def get_file_content_raw(file_link: str) -> str:
    resp = requests.get(file_link)
    if resp.status_code != 200:
        print(f"{file_link} returned with status code {resp.status_code}")
        return ""

    return resp.text
