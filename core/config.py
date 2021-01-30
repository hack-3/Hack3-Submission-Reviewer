import json
import os

with open("storage.json", "a") as f:
    if os.stat("storage.json").st_size == 0:
        f.write("{}")

with open("storage.json", "r") as f:
    data = json.load(f)

    data.setdefault("user", "")
    data.setdefault("password", "")
    data.setdefault("host", "")

    data.setdefault("github", "")

user = data["user"]
password = data["password"]
host = data["host"]

github = data["github"]

disallowed_extensions = {"wav", "zip", "gif", "aia", "pdf", "h5", "caffemodel", "model", "dat", "tar", "pth", "pptx"}

def update_config(user_ = None, password_ = None, host_ = None, github_ = None):
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
