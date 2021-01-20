from hack3 import misc_functions, mysql_functions, webscraping_functions
import tlsh

# # mysql_functions.store_urls_batch(ending_page=9999, max_links=200)
#
# # mysql_functions.hash_descriptions()
#
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
misc_functions.store_projects_batch(ending_page=999, max_links=30)
