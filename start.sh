#!/bin/bash
#rm test_storage.txt
rm documents.db
#rm session.db
rm *.log


trap 'killall' INT

killall() {
    trap '' INT TERM     # ignore INT and TERM while shutting down
    echo "**** Shutting down... ****"     # added double quotes
    kill -TERM 0         # fixed order, send TERM not INT
    wait
    echo DONE
}

python server.py &
#python fetcher.py &

cat # wait forever