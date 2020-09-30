#!/bin/ash
echo $AUTH0_CLIENT | '{print substr($1,1,10)}'
echo $AUTH0_SECRET | awk '{print substr($1,1,5)}'
echo $AUTH0_AUD
if $WORKER ; then
    echo "Is worker"
    supervisord -c  /etc/supervisor/conf.d/worker.conf
else
	echo "Is not worker"
	python /app/manage.py migrate
    supervisord -c  /etc/supervisor/conf.d/api.conf
fi
