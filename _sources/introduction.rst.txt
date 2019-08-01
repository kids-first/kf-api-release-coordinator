Introduction
============

Background
----------

There are several services which drive end user apps in the Kids First
ecosystem.
These services all consume Kids First data and must stay in sync with one and
other in terms of the state of their data. One service cannot have more up to
date data then another service.
Additionally, there may be other services
outside of the Kids First ecosystem that are interested in staying in sync with
the latest Kids First data as new releases get published.

The Kids First Release Coordinator service ensures data consistency among Kids
First data release consumers and is responsible for orchestrating the
synchronization and publishing of a data release.
Data synchronization is the process in which all data release consumers
retrieve the latest release data and stage or store it in an environment/state
where it is not yet accessible to the public.
The publishing of a data release is the process of a data release consumer
making the staged data accessible to the public.


Coordinator and Task Services
-----------------------------

The Kids First Release Coordinator Service consists of two types of services:
The Coordinator Service and Task Services.

Task Services
+++++++++++++

In order for a Kids First data release consumer to stay up to date with data
releases, it must implement a Task Service.
A task service should implement the endpoints in the Kids First Release
Coordinator Task Service specification in order for the release coordinator to
properly invoke tasks.


Coordinator Service
+++++++++++++++++++

The task service endpoints expose a common interface for the Coordinator
Service to communicate with.
Through these endpoints, the Coordinator Service instructs the task services
to perform a sequence of operations that carry out the steps necessary for a
data release to be published.
