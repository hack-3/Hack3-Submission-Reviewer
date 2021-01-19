from hack3 import mysql_functions
import time


def monitor_site():
    """
    Monitors the devpost site to look for recently created projects
    :return: None
    """
    while True:
        print("Request sent")
        mysql_functions.store_urls_batch(ending_page=1, max_links=5)
        time.sleep(30)


