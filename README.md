Kids First Release Coordinator
==============================

The Release Coordinator responds to requests to release data by orchestrating
necessary tasks to execute and sync operations needed for a data release.

[View the spec](http://petstore.swagger.io/?url=https://kids-first.github.io/kf-api-release-coordinator/task.yaml)


Implementing a Task Service
---------------------------

A Task Service is expected to implement certain endpoints that will allow the
Release Coordinator to request task runs and get task status.

[View the spec](http://petstore.swagger.io/?url=https://kids-first.github.io/kf-api-release-coordinator/task.yaml)

![Diagram](https://kids-first.github.io/kf-api-release-coordinator/ReleaseCoordinatorFlow.png)
