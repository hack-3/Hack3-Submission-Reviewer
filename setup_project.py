import json
import subprocess
import sys
import mysql
from mysql.connector import errors

# Gets the required libraries from
# subprocess.check_call([sys.executable, "-m", "pip", "install", "mysql-connector-python"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])

# Gets mysql tables and stuff sort out
user = input("username: ")
password = input("password: ")
host = input("Server ip/host: ")
github_token = input("Github Token: ")

connection = mysql.connector.connect(user=user, password=password, host=host)
cursor = connection.cursor()

try:
    cursor.execute("CREATE DATABASE hack3")
except errors.DatabaseError as e:
    print(e)

connection.database = "hack3"

try:
    cursor.execute(
        "CREATE TABLE projects (url VARCHAR(120) NOT NULL UNIQUE, timeAdded DATETIME, descHash VARCHAR(100) NOT NULL);")
except errors.ProgrammingError as e:
    print(e)

try:
    cursor.execute(
        "CREATE TABLE files (url VARCHAR(120) NOT NULL, timeAdded DATETIME, fileHash VARCHAR(100) NOT NULL, fileName VARCHAR(30), extension VARCHAR(10));")
except errors.ProgrammingError as e:
    print(e)

with open("storage.json", "w") as f:
    json.dump({"user": user, "password": password, "host": host, "github": github_token}, f)
