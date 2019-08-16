Kids First Release Coordinator
==============================

.. image:: /_static/images/release_coordinator.png
   :alt: Kids First Release Coordinator

About
=====

The Kids First Release Coordinator brings different services in the Kids First
ecosystem together to release data in a synchronized manner.

Quickstart
----------

Getting started is easy! To start running instance of the service complete
with data, install
`Docker <https://www.docker.com>`_ and
`Docker Compose <https://docs.docker.com/compose/install>`_ then run:

.. code-block:: bash

    git clone git@github.com:kids-first/kf-api-release-coordinator.git
    cd kf-api-release-coordinator
    docker network create kf-data-stack
    docker-compose up -d


This will and run the release coordinator and supporting services with the
code mounted into the containers for development.
The api will be exposed at `<http://localhost:5000>`_ by default.



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction

.. toctree::
   :maxdepth: 2
   :caption: Release Coordinator:

   release_coordinator/introduction
   release_coordinator/api
   release_coordinator/resources
   release_coordinator/permissions

.. toctree::
   :maxdepth: 2
   :caption: Task Services:

   task_service/introduction
   task_service/api
