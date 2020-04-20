#!/bin/ash
/app/bin/wait-for-pg.sh ${PG_HOST:-pg}

python /app/manage.py migrate

case $PRELOAD_DATA in
    "FAKE")
        echo "Will create fake data"
        /app/manage.py fakedata
        ;;
    *)
        echo "Will not pre-populate database"
        ;;
esac

python /app/manage.py runserver 0.0.0.0:5000
