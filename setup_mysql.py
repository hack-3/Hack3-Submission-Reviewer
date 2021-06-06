from util import configuration, mysql_util, mysql_datatypes as DataType

# Gets mysql tables and stuff sort out
user = input("username: ")
password = input("password: ")
host = input("Server ip/host: ")
github_token = input("Github Token: ")

configuration.update_config(username=user, password=password, host=host, database="hack3", github=github_token)

connection1 = mysql_util.connect()
curs1 = connection1.cursor()

curs1.execute(f"CREATE DATABASE IF NOT EXISTS {configuration.get_database()} ")

connection1.commit()

curs1.close()
connection1.close()

mysql_util.create_table("projects", devpostUrl=DataType.VarChar(120), githubSources=DataType.VarChar(200),
                        timeAdded=DataType.DateTime(), descHash=DataType.VarChar(100), added=DataType.Bool(None),
                        override=False)
mysql_util.command("ALTER TABLE projects ADD PRIMARY KEY (devpostUrl);", commit=True)
mysql_util.command("ALTER TABLE projects ALTER COLUMN added SET DEFAULT FALSE", commit=True)