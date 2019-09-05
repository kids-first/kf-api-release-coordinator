#!/bin/ash
source /app/bin/load_vault.sh

if [[ -n $AUTH0_SECRET]] ; then
    echo "Load AUTH0 secrets from s3"
    aws s3 cp $AUTH0_SECRET ./auth0_secrets.env
    source ./auth0_secrets.env
    rm ./auth0_secrets.env
fi

if $WORKER ; then
    echo "Is worker"
    supervisord -c  /etc/supervisor/conf.d/worker.conf
else
	echo "Is not worker"
	python /app/manage.py migrate
    supervisord -c  /etc/supervisor/conf.d/api.conf
fi
