import mysql
from mysql.connector import errors
from core import config

# Gets mysql tables and stuff sort out
user = input("username: ")
password = input("password: ")
host = input("Server ip/host: ")
github_token = input("Github Token: ")

config.update_config(user, password, host, github_token)

connection = mysql.connector.connect(user=config.user, password=config.password, host=config.host)
cursor = connection.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS hack3")

connection.database = "hack3"

cursor.execute(
    "CREATE TABLE IF NOT EXISTS projects (url VARCHAR(120) NOT NULL UNIQUE, timeAdded DATETIME, descHash VARCHAR(100) NOT NULL);")
cursor.execute(
    "CREATE TABLE IF NOT EXISTS files (githubUrl VARCHAR(120) NOT NULL, devpostUrl VARCHAR(120), timeAdded DATETIME, fileHash VARCHAR(100) NOT NULL, fileName VARCHAR(30), extension VARCHAR(10));")
