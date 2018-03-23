Kids First Release Coordinator
==============================

The Release Coordinator responds to requests to release data by orchestrating
necessary tasks to execute and sync operations needed for a data release.

[View the spec](https://kids-first.github.io/kf-api-release-coordinator/docs/coordinator.html)


Implementing a Task Service
---------------------------

A Task Service is expected to implement certain endpoints that will allow the
Release Coordinator to request task runs and get task status.

[View the spec](https://kids-first.github.io/kf-api-release-coordinator/docs/task.html)

![Diagram](https://kids-first.github.io/kf-api-release-coordinator/ReleaseCoordinatorFlow.png)
