#!/bin/bash
#seq 1 3 | parallel -j 10 python3 main.py store_projects 1 10000
#python3 main.py store_projects 101 200
#python3 main.py store_projects 201 300
#python3 main.py store_projects 301 400
#python3 main.py store_projects 401 500
#python3 main.py store_projects 501 600
#python3 main.py store_projects 601 700
#python3 main.py store_projects 701 800
#python3 main.py store_projects 801 900
#python3 main.py store_projects 901 1000

#echo "Spawning 100 processes"
#for i in {1..100} 
#do
#    (python3 main.py store_projects 101 1000 & )
#done

#parallel ::: python3 main.py store_projects 901 1000 python3 main.py store_projects 801 900


for cmd in "$@"; do {
  echo "Process \"$cmd\" started";
  $cmd & pid=$!
  PID_LIST+=" $pid";
} done

trap "kill $PID_LIST" SIGINT

echo "Parallel processes have started";

wait $PID_LIST

echo
echo "All processes have completed";
