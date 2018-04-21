FROM        python:3-alpine3.7

ADD         requirements.txt /app/
WORKDIR     /app
ENV         WORKER false

RUN apk update && apk add py3-psycopg2 musl-dev \
    nginx supervisor git \
    openssl ca-certificates \
    gcc postgresql-dev \
 && pip install --upgrade pip \
 && pip install virtualenv

RUN         virtualenv -p python3 /app/venv
RUN         source /app/venv/bin/activate \
            && /app/venv/bin/pip install -r /app/requirements.txt
ADD         . /app
RUN         /app/venv/bin/python /app/setup.py install

EXPOSE      80
RUN         /app/venv/bin/python /app/manage.py collectstatic -v0 --noinput


# Setup nginx
RUN         mkdir -p /run/nginx
RUN         mkdir -p /etc/nginx/sites-available
RUN         mkdir /etc/nginx/sites-enabled
RUN         rm -f /etc/nginx/sites-enabled/default
RUN         rm -f /etc/nginx/conf.d/default.conf
COPY        bin/nginx.conf /etc/nginx/nginx.conf

# Setup supervisord
RUN         mkdir -p /var/log/supervisor/conf.d
COPY        bin/worker.conf /etc/supervisor/conf.d/worker.conf
COPY        bin/api.conf /etc/supervisor/conf.d/api.conf

# Start processes
CMD ["/app/bin/run.sh"]
