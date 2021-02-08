import json
import os

# Creating the file if it doesn't exist
with open("storage.json", "a") as f:
    if os.stat("storage.json").st_size == 0:
        f.write("{}")

# Sets default of some data
with open("storage.json", "r") as f:
    data = json.load(f)

    data.setdefault("user", "")
    data.setdefault("password", "")
    data.setdefault("host", "")

    data.setdefault("github", "")

# Information required for mysql connection
user = data["user"]
password = data["password"]
host = data["host"]

# Information to access the github api
github = data["github"]

# A few disallowed extensions
disallowed_extensions = {"wav", "zip", "gif", "aia", "pdf", "h5", "caffemodel", "model", "dat", "tar", "pth", "pptx",
                         "exe", "md", "jpg"}


def update_config(user_=None, password_=None, host_=None, github_=None):
    """
    Internal method to save a config
    :param user_: Username (optional)
    :param password_: Password (optional)
    :param host_: Host IP (optional)
    :param github_: Github Token (optional)
    :return: None
    """
    global user, password, host, github, data

    if user_:
        data["user"] = user_

    if password_:
        data["password"] = password_

    if host_:
        data["host"] = host_

    if github_:
        data["github"] = github_

    user, password, host, github = data["user"], data["password"], data["host"], data["github"]

    with open("storage.json", "w") as f:
        json.dump(data, f)
