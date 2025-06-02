#!/bin/bash

cd "$(dirname "$0")"
./connect-db.sh < clean-db.sql

for sql_file in $(find ../db/init_updt/*.sql -type f | sort -V); do
    if [ -f "$sql_file" ]; then
        ./connect-db.sh < "$sql_file"
    fi
done