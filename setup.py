import json
import subprocess
import sys

from mysql.connector import errors
from hack3.mysql_setup_functions import (create_database,
                                         create_url_table)

# Gets the required libraries from
subprocess.check_call([sys.executable, "-m", "pip", "install", "mysql-connector-python"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])

# Gets mysql tables and stuff sort out

user = input("username: ")
password = input("password: ")
host = input("Server ip/host: ")

try:
    create_database(user, password, host)
except errors.DatabaseError:
    pass

try:
    create_url_table(user, password, host)
except errors.ProgrammingError:
    pass

with open("storage.json", "w") as f:
    json.dump({"user": user, "password": password, "host": host}, f)