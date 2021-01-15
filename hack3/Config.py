import json


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)

            with open("hack3/storage.json", "r") as f:
                data = json.loads(f.read())

            cls.user = data["user"]
            cls.password = data["password"]
            cls.host = data["host"]
        return cls._instance


if (__name__ == "__main__"):
    config = Config()
    print(config.user)
    print(config.password)
    print(config.host)
