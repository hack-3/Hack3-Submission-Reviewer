import sys
from util import util


sys.argv.pop(0)

if len(sys.argv) == 0:
    print("python main.py [store_projects|check_project]")
else:
    if sys.argv[0] not in ("store_projects", "check_project"):
        print("python main.py [store_projects|check_project]")
    else:
        if sys.argv[0] == "store_projects":
            # python main.py store_projects - stores page 1
            # python main.py store_projects 1 10 - stores page 1-10 inclusive

            starting_page = 1
            ending_page = 1

            if len(sys.argv) > 1:
                if sys.argv[1] == "-h":
                    print("python main.py store_projects (starting_page) (ending_page)")
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
            # python main.py check_project https://devpost.com/software/test - checks the project, outputs it to output.txt

            if len(sys.argv) == 1:
                print("python main.py check_project (project_url)")
            else:
                if sys.argv[1] == "-h":
                    print("python main.py check_project (project_url)")
                else:
                    util.check_project(sys.argv[1])
