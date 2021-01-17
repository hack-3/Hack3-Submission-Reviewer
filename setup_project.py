import json
import subprocess
import sys

from mysql.connector import errors
from hack3.mysql_setup_functions import create_database, execute_query

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
    execute_query(user, password, host, "CREATE TABLE project_url (url VARCHAR(120) NOT NULL UNIQUE, time DATETIME);")
except errors.ProgrammingError:
    pass

try:
    execute_query(user, password, host, "CREATE TABLE project_data (url VARCHAR(120) NOT NULL UNIQUE, time DATETIME, descCompress VARCHAR(200));")
except errors.ProgrammingError:
    pass

with open("storage.json", "w") as f:
    json.dump({"user": user, "password": password, "host": host}, f)
