![kf](/static/kf_releasecoordinator.png)

The Kids First Release Coordination brings different services in the Kids First
ecosystem together to release data in a synchronized manner.

## Background
There are several services which drive end user applications in the Kids First
ecosystem. These services all consume Kids First data and must stay in sync
with one another in terms of the state of their data. One service cannot have
more up to-date data than another service. Additionally, there may be other 
services outside of the Kids First ecosystem that are interested in staying in
sync with the latest Kids First data as new releases get published. The Kids
First Release Coordinator service ensures data consistency among Kids First 
data release consumers and is responsible for orchestrating the synchronization
and publishing of a data release. Data synchronization is the process in which
all data release consumers retrieve the latest release data and stage or store
it in an environment/state where it is not yet accessible to the public.
The publishing of a data release is the process of a data release consumer
making the staged data accessible to the public.

### The Release Process

Publishing a release consists of 3 steps:

1. Task initialization
    * The coordinator service will send a `POST` with `action=initialize` to each
      task service's `/tasks` endpoint and inform it of the `release_id`
      and `task_id`.
    * The coordinator service will check the response of each task service and
      ensure each repsoned successfully with `state=pending`
2. Staging of release data
    * The coordinator will send a `POST` with `action=start` to each task
      service's `/tasks` endpoint and expect the task service to respond
      successfully with `state=running`
    * The task services will run their task completing the work necessary to
      stage the studies in the release
    * The Coordinator will continuously ping any `running` tasks at this time
      for their status using a `POST`ed `action=get_status` to the `/tasks`
      endpoint. Any non-`200` status will be interpreted as the task having
      failed.
    * The Coordinator will wait until all tasks have updated the coordinator
      with `state=staged`
3. Publishing of release data
    * Once the release has been `staged`, and the results have been manually
      reviewed, a request to the Coordinator`s `/<release_id>/publish` endpoint
      will trigger the publication of that release.
    * Upon receiving a publish request from the user, the coordinator will send
      a POST with `action=publish` to each of the registered endpoints.
    * The task services will begin publishing the staged release data. The task
      services will set `state=publishing` during this step.
    * The Coordinator will continuously ping any `publishing` tasks at this time
      for their status using a `POST`ed `action=get_status` to the `/tasks`
      endpoint. Any non-`200` status will be interpreted as the task having
      failed.
    * Once all task services have responded with `state=published`,
      the release is considered finished and published.

The diagram below illustrates the sequence of operations between the Coordinator
service and a Task service for a successful release publish.
![Diagram](/static/ReleaseCoordinatorFlow.png)

### Handling Failures

#### Health check polling

The Coordinator will continuously poll all tasks in the `running` or
`publishing` state. Any non-`200` response seen during this time will cause
the coordinator to assume that task has failed, and will consequently signal
the related release to fail, and cancelling all other tasks ascociated with it.

#### Explicit task failures

If a task has recognized that it has failed, it may explicitly report to the
Coordinator by updating its state with `state=failed`. This will cause the
related release to fail and cancel all other tasks in the release.

#### Cancelling of a release

A release may be cancelled at any time. When this occures, the Coordinator
will inform all tasks in the release by `POST`ing an `action=cancel` with the
`task_id` to each service.
