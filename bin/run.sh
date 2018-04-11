#!/bin/ash
source venv/bin/activate
python manage.py migrate
supervisord -c  /etc/supervisor/conf.d/supervisord.conf
