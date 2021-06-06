from util import configuration, mysql_util, mysql_datatypes as DataType

# Gets mysql tables and stuff sort out
user = input("username: ")
password = input("password: ")
host = input("Server ip/host: ")
github_token = input("Github Token: ")

configuration.update_config(username=user, password=password, host=host, database="hack3", github=github_token)

mysql_util.create_table("projects", devpostUrl=DataType.VarChar(120), githubSources=DataType.VarChar(200),
                        timeAdded=DataType.DateTime(), descHash=DataType.VarChar(100), added=DataType.Bool(False),
                        override=False)

connection = mysql_util.connect()
curs = connection.cursor()

curs.execute("ALTER TABLE projects ADD PRIMARY KEY (devpostUrl);")
curs.execute("ALTER TABLE projects ALTER COLUMN added SET DEFAULT FALSE")

connection.commit()

curs.close()
connection.close()