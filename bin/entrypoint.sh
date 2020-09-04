#!/bin/ash

if $WORKER ; then
    echo "Is worker"
    supervisord -c  /etc/supervisor/conf.d/worker.conf
else
	echo "Is not worker"
	python /app/manage.py migrate
    supervisord -c  /etc/supervisor/conf.d/api.conf
fi
