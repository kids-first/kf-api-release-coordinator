Development
===========

Developing with Docker
----------------------

The Release Coordinator includes a ``docker-compose.yml`` file that is
configured to quickly get started with running and developing on the codebase.
Running ``docker-compose up`` from the root directory will start up the
Coordinator and dependent services such as a postgres database, redis, a task
runner, and a task scheduler.
The codebase will also be mounted into the running services so that development
changes may be reflected immediately.

Changing Settings
-----------------

The Coordinator includes three settings files by default: development,
testing, and production.
When run using ``docker-compose``, the Coordinator will default to the
``testing`` settings, which will enforce authentication and permissions
checking.
The settings that the Coordinator runs with may be configured with the
``DJANGO_SETTINGS_MODULE`` environment variable.
For example, when running with ``docker-compose``:

.. code::

   DJANGO_SETTINGS_MODULE=coordinator.settings.testing docker-compose up

Often, it's desirable to want full access to the api without having to
configure an authentication backend or gain access to an existing one.
To do this, the ``development`` settings may be used which will automatically
authenticate every request as an ``ADMIN`` user and giving complete access to
the api.

Generating Mock Data
--------------------

When running with ``docker-compose``, the Coordinator will automatically
bootstrap the database with a number of fake entries to enable faster
development.
This setting may be overridden by providing any value other than ``FAKE`` for
the ``PRELOAD_DATA`` environment variable.
The mock data is generated through a Django management command, ``fakedata``,
which may be run by itself if developing outside of docker:

.. code::

   python manage.py fakedata
