FROM        python:3.7-alpine3.7 as base

ADD         requirements.txt /app/
WORKDIR     /app
ENV         WORKER false

RUN apk --update add py3-psycopg2 \
    musl-dev \
    supervisor \
    git \
    ca-certificates \
    libffi-dev \
    libressl-dev \
    gcc \
    postgresql-dev \
    postgresql-client \
 && pip install --upgrade pip

# Python deps
RUN         pip install -r /app/requirements.txt 
RUN         pip install awscli

ADD         . /app

# Bake version number
RUN         COMMIT=`git rev-parse --short HEAD` && echo "COMMIT=\"${COMMIT}\"" > /app/coordinator/version_info.py \
            && VERSION=`git describe --always --tags` && echo "VERSION=\"${VERSION}\"" >> /app/coordinator/version_info.py


RUN         python /app/setup.py install \
            && python /app/manage.py collectstatic -v0 --noinput

EXPOSE      80

# Setup supervisord
RUN         mkdir -p /var/log/supervisor/conf.d
COPY        bin/worker.conf /etc/supervisor/conf.d/worker.conf
COPY        bin/api.conf /etc/supervisor/conf.d/api.conf


# Start processes
CMD ["/app/bin/entrypoint.sh"]


FROM base as dev
COPY        dev-requirements.txt /app/
RUN         pip install -r /app/dev-requirements.txt


# Production stage containing vault to load secrets
FROM base as prd

RUN apk --update add jq wget

RUN wget -q -O vault.zip https://releases.hashicorp.com/vault/1.0.3/vault_1.0.3_linux_amd64.zip \ 
    && unzip vault.zip \
    && mv vault /usr/local/bin

CMD ["/app/bin/entrypoint.sh"]
