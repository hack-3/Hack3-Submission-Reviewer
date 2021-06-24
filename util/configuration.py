import json, os

config_file = "storage.json"
# config_file = input("Configuration file: ")

if not os.path.isfile(config_file):
    with open(config_file, "w") as f:
        f.write("{}")

with open(config_file, "r") as f:
    data = json.load(f)


def get_username():
    return data["user"]


def get_password():
    return data["password"]


def get_host():
    return data["host"]


def get_database():
    return data["database"]


def get_github_token():
    return data["github"]


def update_config(username=None, password=None, host=None, database=None, github=None):
    if username:
        data["user"] = username

    if password:
        data["password"] = password

    if host:
        data["host"] = host

    if database:
        data["database"] = database

    if github:
        data["github"] = github

    with open(config_file, "w") as f:
        json.dump(data, f)
