<p align="center">
  <img src="docs/kf_releasecoordinator.png">
</p>
<p align="center">
  <a href="https://github.com/kids-first/kf-api-release-coordinator/blob/master/LICENSE"><img src="https://img.shields.io/github/license/kids-first/kf-api-release-coordinator.svg?style=for-the-badge"></a>
  <a href="https://kids-first.github.io/kf-api-release-coordinator/docs/coordinator.html"><img src="https://img.shields.io/readthedocs/pip.svg?style=for-the-badge"></a>
  <a href="https://circleci.com/gh/kids-first/kf-api-release-coordinator"><img src="https://img.shields.io/circleci/project/kids-first/kf-api-release-coordinator.svg?style=for-the-badge"></a>
  <a href="https://app.codacy.com/app/kids-first/kf-api-release-coordinator/dashboard"><img src="https://img.shields.io/codacy/grade/7500ec3e7b81489dbe0ff0cee8c3d76d.svg?style=for-the-badge"></a>
</p>

Kids First Release Coordinator
==============================

The Kids First Release Coordinator brings different services in the Kids First ecosystem together to release data in a synchronized manner.


## Development Quick Start

Getting up and running with a fully functional Release Coordinator is as easy as:
```
git clone https://github.com/kids-first/kf-api-release-coordinator
cd kf-api-release-coordinator
docker-compose up -d
```


This will stand up a couple different services:
- The Coordinator API on port `5000`
- A task worker to process different release jobs
- A redis instance to manage the work queue
- A postgres database to store information about releases, tasks, and services
- A simple scheduler that will ping `/heath_checks`


## Install for Development

The above quicstart is great for developing services against the Coordinator,
however, it is not ideal for developing new features for the coordinator itself.
To do that, a redis and postgres instance must be setup locally to develop
against:

```
docker run -d -p 5432:5432 --name coordinator-pg postgres:9.5
docker run -d --name coordinator-redis -p 6379:6379 redis:latest
docker exec coordinator-pg psql -U postgres -c "CREATE DATABASE dev;"
```

If different ports are desired, change the bindings on the docer containers and
modify `coordinator/settings.py` to reflect them.

Next, install the python environment:
```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r dev-requirements.txt
pip install -r requirements.txt
```
And then initialize the database:
```
python manage.py migrate
```

You should now be able to run the Coordinator service locally:
```
python manage.py runserver
```

## Migrations

When the data model is changed, a new migration must be made and applied
before running the service or any tests:
```
python manage.py makemigrations api
```


## Testing


Make sure to specify the test settings file when running tests
```
pytest --ds=tests.settings --pep8
```
