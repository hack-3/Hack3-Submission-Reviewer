from hack3 import mysql_functions
import tlsh

# mysql_functions.hash_descriptions()

connection = mysql_functions.get_connection()
cursor = connection.cursor()

cursor.execute("SELECT url, descHash FROM project_description")
things = [i for i in cursor]

cursor.close()
connection.close()

for i, j in enumerate(things):
    for l in things[i+1:]:
        diff = tlsh.diff(j[1], l[1])

        if diff < 50:
            print(j[0], l[0], diff)