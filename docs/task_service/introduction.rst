Introduction
============

A task service runs a function that is a step in the release process such as:
Rolling over version numbers, updating file states for download, and making
new data visible to users.
These tasks should expose a common interface for the Coordination Service to
communicate with.
A task service should implement the endpoints in this specification in order
for the release coordinator to properly invoke tasks.

Current Task Services
---------------------

**Portal ETL** - The portal ETL is run to generate elasticsearch indices that
serve the portal front end

**Cavatica File Sync** - Files need to be synced with Cavatica during a
release so that they may be available in Cavatica

**Release Reports** - Generates summary statistics of studies in a release

**Snapshot Service** - Scrapes the state of the dataservice at the time of a
release


Examples
--------

There is currently the `Task Reference <https://github.com/kids-first/kf-task-reference>`_
repository which implements a very basic task service.

The `Release Reports <https://github.com/kids-first/kf-task-release-reports>`_
task service demonstrates a simple implementation of a real-world task service
that uses AWS lambda and Dynamo db for a light-weight deployment.
