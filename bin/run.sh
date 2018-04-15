#!/bin/ash
source venv/bin/activate
if $WORKER ; then
    echo "Is worker"
    supervisord -c  /etc/supervisor/conf.d/worker.conf
else
	echo "Is not worker"
	python manage.py migrate
    supervisord -c  /etc/supervisor/conf.d/api.conf
fi
