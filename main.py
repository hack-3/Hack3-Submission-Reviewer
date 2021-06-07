from util import util

a = input("What would you like to do? (add projects, add files, check project): ")

if a == "add projects":
    util.store_projects_batch(ending_page=1)
elif a == "add files":
    util.store_project_sources()
elif a == "check project":
    util.check_project(input("Devpost url: "))