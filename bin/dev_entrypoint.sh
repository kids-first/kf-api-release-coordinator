#!/bin/ash
/app/bin/wait-for-pg.sh pg
python /app/manage.py migrate
python /app/manage.py runserver 0.0.0.0:5000
