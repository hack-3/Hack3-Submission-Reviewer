import sys
from util import util

def get_default_message():
    return "python main.py [store_project|store_sources|check_project]"

sys.argv.pop(0)

if len(sys.argv) == 0:
    print(get_default_message())
else:
    if sys.argv[0] not in ("store_project", "store_sources", "check_project"):
        print(get_default_message())
    else:
        if sys.argv[0] == "store_project":
            starting_page = 1
            ending_page = 1

            if len(sys.argv) > 1:
                if sys.argv[1] == "-h":
                    print("python main.py store_project (starting_page) (ending_page)")
                else:
                    starting_page = int(sys.argv[1])
                    ending_page = int(sys.argv[2]) if len(sys.argv) >= 3 else starting_page + 1

            util.store_projects_batch(starting_page=starting_page, ending_page=ending_page)
        elif sys.argv[0] == "store_sources":
            if len(sys.argv) > 1 and sys.argv[1] == "-h":
                print("python main.py store_sources")
            else:
                util.store_project_sources()
        else:
            if len(sys.argv) == 1:
                print("python main.py check_project (project_url)")
            else:
                if sys.argv[1] == "-h":
                    print("python main.py check_project (project_url)")
                else:
                    print(util.check_project(sys.argv[1]))
