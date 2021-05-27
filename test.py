from util import mysql_functions, webscraping_functions, misc_functions, core_functions

# # mysql_functions.store_urls_batch(ending_page=9999, max_links=200)
#
# # mysql_functions.hash_descriptions()

# connection = mysql_functions.get_connection()
# cursor = connection.cursor()
#
# cursor.execute("SELECT url, descHash FROM project_description")
# # cursor.execute("SELECT url, descHash FROM project_description")
# things = [i for i in cursor if i[1][0] != "N"]
#
# cursor.close()
# connection.close()
#
# # print(things)
#
# for i, j in enumerate(things):
#
#     for l in things[i+1:]:
#
#         diff = tlsh.diff(j[1], l[1])
#
#         if diff < 50:
#             print(j[0], l[0], diff)

# misc_functions.monitor_site()
# misc_functions.store_projects_batch(ending_page=999, max_links=100)


# misc_functions.store_github(cursor, "https://github.com/masoudhassani/river_raid", "https://devpost.com/software/atari-riverraid-played-by-ai")
#
# connection.commit()
#
# cursor.close()
# connection.close()

# misc_functions.store_files()
# print(webscraping_functions.get_links("https://devpost.com/software/coursecake"))

# misc_functions.check_project("https://devpost.com/software/multi-camera-smart-surveillance-network-xypa6j")
# misc_functions_old.store_projects_batch(starting_page=1, ending_page=999, max_links=5)
# misc_functions.store_files()

# print(webscraping_functions.get_links("https://devpost.com/software/dr-helper"))

# con = mysql_functions.get_connection()
# curs = con.cursor()

import time
#
start = time.time()
#
url = "https://devpost.com/software/test2-vpbr5s"
#
print(core_functions.check_file(url))
print(time.time() - start)

# core_functions.store_projects_batch(max_links=50)
# core_functions.store_files()
# print(webscraping_functions.get_links("https://devpost.com/software/hocus-focus-64xe8c"))

# desc_hash = misc_functions.get_description_hash(url)
# mysql_functions.store_project(curs, url, desc_hash)

# core_functions.store_projects_batch(max_links=5)

# core_functions.store_files()

# con.commit()
# con.close()
# curs.close()