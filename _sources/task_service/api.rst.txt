Task Service API
================

Below is documented the API specification that Task Services must follow
in order to be utilized by the Release Coordinator.


.. http:GET:: /status

    Returns information about the Task service including the current status.
    This endpoint is used by the Coordinator to determine the health of the task
    service. Any non-``200`` response will imply that the service is
    unavailable. If enough consecutive non-``200`` responses are received by the
    Coordinator, then any tasks that may have been issued to the task service
    will be assumed as failed.

    :>json string name: The name of the task service
    :>json string message: A status message
    :>json string version: The software version of the task service

    :status 200: Ready to receive tasks
    :status 503: Service unavailable

    **Example**:

    .. http:example:: curl

       GET /status HTTP/1.1
       Host: kf-task-servec.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
            "name": "datamodel rollover",
            "message": "ready for work",
            "version": "2.0.4"
       }


.. http:post:: /tasks

    The primary endpoint for communicating with a Service

    :<json string action: Action the action or procedure to run
    :<json string task_id: The ``kf_id`` of the task instance to perform the
        action on
    :<json string release_id: The ``kf_id`` of the task's related release

    :>json string name: The name of the task service
    :>json string kf_id: The ``kf_id`` for which the action was performed
    :>json string release_id: The ``kf_id`` of the release related to the task
    :>json string state: The current state of the task
    :>json int progress: The Percentage completion of the task
    :>json date date_submitted: The date at which the Service recieved the task

    :status 200: Action accepted
    :status 400: Invalid input
    :status 404: Task not found
    :status 503: Action rejected

    **Example**:

    .. http:example:: curl

       POST /tasks HTTP/1.1
       Host: kf-task-servec.kidsfirstdrc.org
       Accept: application/json

       {
            "action": "start",
            "task_id": "TA_3G2409A2",
            "release_id": "RE_AB28FG90"
       }


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
            "name": "data model rollover",
            "kf_id": "TA_3G2409A2",
            "release_id": "RE_AB28FG90",
            "state": "running",
            "progress": "50%",
            "date_submitted": "2018-03-19T20:12:24.702813+00:00"
       }


The Release Coordinator will use this endpoint to communicate all actions (via
a ``POST``) that the task service must take during the release publish. When a
release is begun, the Release Coordinator service will send a ``POST`` to this
endpoint with an ``initialize`` action. The task service should set its state
to pending and respond with a status code ``200``. The Coordinator will expect
a ``200`` response from all task services in the release to continue with the
release process.

If any non-``200`` response is returned, the Coordinator will cancel the
release.

Once the Coordinator has verified that all tasks are ready for work, it will
signal the task service to begin staging data via a ``POST`` with action set to
``start``. Upon receiving the ``start`` action, the task service should begin
staging the data and set it's state to running.

During the staging process the Release Coordinator will poll the task service
for status via a ``POST`` and action set to ``get_status``. The task service
should respond with its latest state and progress. If any non-``200`` response
is returned, the Coordinator will cancel the release. Once work is completed,
the task should set its state to staged and task service should notify the
Coordinator with its new state.

When its time for the data release to be made public, the Coordinator will
signal the task service to begin publishing via a ``POST`` to this endpoint
with action set to ``publish``. Upon receiving the ``publish`` action, the task
service should set it's state to publishing. Once again, the Release
Coordinator will poll the task service for status via a ``POST`` and action set
``to get_status``. If any non-``200`` response is returned, the Coordinator
will cancel the release.

If a task ever needs to be explicitly stopped at any point in time due to a
failure of any kind, the task service may set its state to failed. If the
release is ever halted due to an explicit stop or because of a failure in any
task, the Coordinator will issue a ``cancel`` action to all task services
informing them to stop their task or discard any operations.

Task Actions
------------

To summarize, the possible actions in a ``POST`` to this endpoint are:

 - ``initialize``
 - ``start``
 - ``publish``
 - ``get_status``
 - ``cancel``

Task States
-----------

The possible states of a task are:

 - ``pending`` - Received the ``initialize`` action, but waiting for start
 - ``running`` - After ``start`` action while the task is processing
 - ``staged`` - After completing work
 - ``publishing`` - While publicizing work
 - ``published`` - After successfully publishing
 - ``canceled`` - Task was canceled by coordinator
 - ``failed`` - Task failed at some stage

Authentication
--------------

To ensure that a request to the task service originates from the coordinator,
all requests to the task services will be made with a Authorization header
containing a bearer jwt for ego. This token may be used to verify the
coordinator's identity against ego using the /oauth/token/verify endpoint.

