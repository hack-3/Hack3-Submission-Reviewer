from hack3.misc_functions import *

type_ = input("xx: ")

if type_ == "batch":
    store_projects_batch(ending_page=999, max_links=500)
elif type_ == "monitor":
    monitor_site()
elif type_ == "source":
    store_files()