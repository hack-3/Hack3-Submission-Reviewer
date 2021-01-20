import json


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)

            with open("storage.json", "r") as f:
                data = json.loads(f.read())

            cls.user = data["user"]
            cls.password = data["password"]
            cls.host = data["host"]
            cls.github = data["github"]

        return cls._instance
