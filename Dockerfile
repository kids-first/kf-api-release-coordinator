FROM        python:3-alpine3.7

ADD         requirements.txt /app/
WORKDIR     /app

RUN apk update && apk add py3-psycopg2 musl-dev \
    nginx supervisor git \
    openssl ca-certificates \
    gcc postgresql-dev \
 && pip install --upgrade pip \
 && pip install virtualenv

RUN         pip install -r /app/requirements.txt
ADD         . /app
RUN         python /app/setup.py install

EXPOSE      80
RUN         python /app/manage.py collectstatic -v0 --noinput


# Setup nginx
RUN         mkdir -p /run/nginx
RUN         mkdir -p /etc/nginx/sites-available
RUN         mkdir /etc/nginx/sites-enabled
RUN         rm -f /etc/nginx/sites-enabled/default
RUN         rm -f /etc/nginx/conf.d/default.conf
COPY        bin/nginx.conf /etc/nginx/nginx.conf

# Setup supervisord
RUN         mkdir -p /var/log/supervisor/conf.d
COPY        bin/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start processes
CMD ["/app/bin/run.sh"]
