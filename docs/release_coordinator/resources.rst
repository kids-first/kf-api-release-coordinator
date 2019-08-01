Resources and Endpoints
=======================


Tasks
-----

Tasks encapsulate individual invocations of a task service made per release.
The Release Coordinator will create new tasks for each enabled service during
the creation of a new release and will follow up with each service throughout
the lifetime of the task.

.. http:get:: /tasks

    Returns a list of tasks

    :query limit: Number of results to return in a page, defaults to 10
    :query offset: How many items to offset the page by
    :query release: Filter tasks related to a given release's kf_id
    :query task_service: Filter tasks related to a given task service's kf_id
    :query state: Filter tasks by a given state

    **Example**:

    .. http:example:: curl

       GET /tasks?release=RE_C6PTRN2K&task_service=TS_WPEKCZHQ HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "count": 1,
           "next": null,
           "previous": null,
           "results": [
               {
                   "kf_id": "TA_WAAE3ZBN",
                   "state": "canceled",
                   "progress": 0,
                   "release": "https://kf-release-coord.kidsfirstdrc.org/releases/RE_C6PTRN2K",
                   "task_service": "https://kf-release-coord.kidsfirstdrc.org/task-services/TS_WPEKCZHQ",
                   "created_at": "2018-09-13T19:48:49.467518Z",
                   "service_name": "Portal ETL Task Service"
               }
           ]
       }


.. http:patch:: /tasks/(kf_id)

    Updates a task of ``kf_id`` with state or progress.
    Use by task services to report progress or status of one of the tasks.

    :<json string state: The state of the task
    :<json int progress: The percentage of completion of the task

    **Example**:

    .. http:example:: curl

       PATCH /tasks/TA_WAAE3ZBN HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json

       {
           "state": "staged",
           "progress": 100
       }


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "kf_id": "TA_WAAE3ZBN",
           "state": "staged",
           "progress": 100,
           "release": "https://kf-release-coord.kidsfirstdrc.org/releases/RE_C6PTRN2K",
           "task_service": "https://kf-release-coord.kidsfirstdrc.org/task-services/TS_WPEKCZHQ",
           "created_at": "2018-09-13T19:48:49.467518Z",
           "service_name": "Portal ETL Task Service"
       }


Task Services
-------------

Task Services are services that perform an action that is required during a
release.
Task Services are required to expose a consistent interface to the tasks that
they have been assigned by the Release Coordinator so that the Release
Coordinator may provide an accurate view into the overall state of a release.

.. http:get:: /task-services

    Lists task services.

    :query limit: Number of results to return in a page, defaults to 10
    :query offset: How many items to offset the page by
    :query enabled: Filter by whether a task service is enabled or not.
        ``True`` or ``False``.

    **Example**:

    .. http:example:: curl

       GET /task-services?enabled=False HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
            "count": 1,
            "next": null,
            "previous": null,
            "results": [
                {
                    "kf_id": "TS_P4QEPHZT",
                    "name": "Snapshot Task Service",
                    "description": "The snapshot task service creates a data dump directly against the data service, given a specific version of data release. The data snapshot is available via Amazon S3 in a JSON form.",
                    "last_ok_status": 0,
                    "author": "meen",
                    "health_status": "ok",
                    "url": "http://kf-task-snapshot",
                    "created_at": "2018-09-11T15:23:46.922950Z",
                    "enabled": false
                }
            ]
        }

.. http:get:: /task-services/(kf_id)

    Get task service of ``kf_id``.

    **Example**:

    .. http:example:: curl

       GET /task-services/TS_WPEKCZHQ HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "kf_id": "TS_WPEKCZHQ",
           "name": "Portal ETL Task Service",
           "description": "Run ETL to update ES indexes with latest data from Data Service.",
           "last_ok_status": 0,
           "author": "jon",
           "health_status": "ok",
           "url": "http://etl-task-service-prd",
           "created_at": "2018-09-13T17:00:09.859959Z",
           "enabled": true
       }


.. http:post:: /task-services

    Register a new task service.
    The coordinator will attempt to ping the ``/status`` endpoint on the
    provided url to verify that the task service can be reached. If there
    is no response, or an error trying to get a response, the task service
    will not be registered and the response will respond with a 400.

    :<json string name: The name of the new task service.
    :<json string description: The description of the new task service.
    :<json string autho: The author of the task service.
    :<json string url: The url of the task service.

    **Example**:

    .. http:example:: curl

       POST /task-services HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json

       {
           "name": "Portal ETL Task Service",
           "description": "Run ETL to update ES indexes with latest data from Data Service.",
           "author": "jon",
           "url": "http://etl-task-service-prd"
       }


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "kf_id": "TS_WPEKCZHQ",
           "name": "Portal ETL Task Service",
           "description": "Run ETL to update ES indexes with latest data from Data Service.",
           "last_ok_status": 0,
           "author": "jon",
           "health_status": "ok",
           "url": "http://etl-task-service-prd",
           "created_at": "2018-09-13T17:00:09.859959Z",
           "enabled": true
       }


.. http:patch:: /task-services

    Updates a task service of ``kf_id``.

    :<json string name: The name of the new task service.
    :<json string description: The description of the new task service.
    :<json string autho: The author of the task service.
    :<json string url: The url of the task service.

    **Example**:

    .. http:example:: curl

       PATCH /task-services/TS_WPEKCZHQ HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json

       {
           "name": "Portal ETL Task Service",
           "description": "Run ETL to update ES indexes with latest data from Data Service.",
           "author": "jon",
           "url": "http://etl-task-service-prd"
       }


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "kf_id": "TS_WPEKCZHQ",
           "name": "Portal ETL Task Service",
           "description": "Run ETL to update ES indexes with latest data from Data Service.",
           "last_ok_status": 0,
           "author": "jon",
           "health_status": "ok",
           "url": "http://etl-task-service-prd",
           "created_at": "2018-09-13T17:00:09.859959Z",
           "enabled": true
       }


.. http:delete:: /task-services/(kf_id)

    Deletes a task service of ``kf_id``.

    **Example**:

    .. http:example:: curl

       DELETE /task-services/TS_WPEKCZHQ HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept


Releases
--------


.. http:get:: /releases

    Lists releases.

    :query limit: Number of results to return in a page, defaults to 10
    :query offset: How many items to offset the page by
    :query state: Filter tasks by a given state

    **Example**:

    .. http:example:: curl

       GET /releases?state=published HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
            "count": 1,
            "next": "http://kf-release-coord-dev.kidsfirstdrc.org/releases?state=published",
            "previous": null,
            "results": [
                {
                    "kf_id": "RE_EJTE6XDS",
                    "name": "Test Auth",
                    "description": "",
                    "notes": [],
                    "state": "published",
                    "studies": [
                        "SD_ME0WME0W"
                    ],
                    "tasks": [
                        {
                            "kf_id": "TA_T4D9PMPJ",
                            "state": "published",
                            "progress": 0,
                            "release": "http://kf-release-coord-dev.kidsfirstdrc.org/releases/RE_EJTE6XDS",
                            "task_service": "http://kf-release-coord-dev.kidsfirstdrc.org/task-services/TS_8DSD3XHF",
                            "created_at": "2018-11-07T16:32:43.563546Z",
                            "service_name": "Reports Task Service"
                        }
                    ],
                    "version": "0.7.0",
                    "created_at": "2018-11-07T16:32:43.271141Z",
                    "tags": [],
                    "author": "daniel",
                    "is_major": false
                }
            ]
        }


.. http:get:: /releases/(kf_id)

    Gets a release of ``kf_id``.

    **Example**:

    .. http:example:: curl

       GET /releases/RE_EJTE6XDS HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "kf_id": "RE_EJTE6XDS",
           "name": "Test Auth",
           "description": "",
           "notes": [],
           "state": "published",
           "studies": [
               "SD_ME0WME0W"
           ],
           "tasks": [
               {
                   "kf_id": "TA_T4D9PMPJ",
                   "state": "published",
                   "progress": 0,
                   "release": "http://kf-release-coord-dev.kidsfirstdrc.org/releases/RE_EJTE6XDS",
                   "task_service": "http://kf-release-coord-dev.kidsfirstdrc.org/task-services/TS_8DSD3XHF",
                   "created_at": "2018-11-07T16:32:43.563546Z",
                   "service_name": "Reports Task Service"
               }
           ],
           "version": "0.7.0",
           "created_at": "2018-11-07T16:32:43.271141Z",
           "tags": [],
           "author": "daniel",
           "is_major": false
       }


.. http:post:: /releases

    Start a new release.
    This will begin a release by creating new tasks for each service.

    :<json string name: The name of the new release.
    :<json string description: The description of the new release.
    :<json boolean is_major: Whether the release is major or not.
    :<json string author: The author of the release.
    :<json array studies: An array of study ``kf_id`` s to include in the
       release

    **Example**:

    .. http:example:: curl

       PATCH /releases/RE_EJTE6XDS HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json

       {
           "name": "My Release",
           "description": "New description,
       }


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "kf_id": "RE_EJTE6XDS",
           "name": "My Release",
           "description": "New description",
           "notes": [],
           "state": "published",
           "studies": [
               "SD_ME0WME0W"
           ],
           "tasks": [
               {
                   "kf_id": "TA_T4D9PMPJ",
                   "state": "published",
                   "progress": 0,
                   "release": "http://kf-release-coord-dev.kidsfirstdrc.org/releases/RE_EJTE6XDS",
                   "task_service": "http://kf-release-coord-dev.kidsfirstdrc.org/task-services/TS_8DSD3XHF",
                   "created_at": "2018-11-07T16:32:43.563546Z",
                   "service_name": "Reports Task Service"
               }
           ],
           "version": "0.7.0",
           "created_at": "2018-11-07T16:32:43.271141Z",
           "tags": [],
           "author": "daniel",
           "is_major": false
       }


.. http:patch:: /releases/(kf_id)

    Update a release of ``kf_id``.

    **Example**:

    .. http:example:: curl

       PATCH /releases/RE_EJTE6XDS HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json

       {
           "name": "My Release",
           "description": "New description,
       }


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "kf_id": "RE_EJTE6XDS",
           "name": "My Release",
           "description": "New description",
           "notes": [],
           "state": "published",
           "studies": [
               "SD_ME0WME0W"
           ],
           "tasks": [
               {
                   "kf_id": "TA_T4D9PMPJ",
                   "state": "published",
                   "progress": 0,
                   "release": "http://kf-release-coord-dev.kidsfirstdrc.org/releases/RE_EJTE6XDS",
                   "task_service": "http://kf-release-coord-dev.kidsfirstdrc.org/task-services/TS_8DSD3XHF",
                   "created_at": "2018-11-07T16:32:43.563546Z",
                   "service_name": "Reports Task Service"
               }
           ],
           "version": "0.7.0",
           "created_at": "2018-11-07T16:32:43.271141Z",
           "tags": [],
           "author": "daniel",
           "is_major": false
       }


.. http:delete:: /releases/(kf_id)

    Cancels a release of ``kf_id``.

    **Example**:

    .. http:example:: curl

       DELETE /releases/RE_EJTE6XDS HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "kf_id": "RE_EJTE6XDS",
           "name": "Test Auth",
           "description": "",
           "notes": [],
           "state": "canceling",
           "studies": [
               "SD_ME0WME0W"
           ],
           "tasks": [
               {
                   "kf_id": "TA_T4D9PMPJ",
                   "state": "published",
                   "progress": 0,
                   "release": "http://kf-release-coord-dev.kidsfirstdrc.org/releases/RE_EJTE6XDS",
                   "task_service": "http://kf-release-coord-dev.kidsfirstdrc.org/task-services/TS_8DSD3XHF",
                   "created_at": "2018-11-07T16:32:43.563546Z",
                   "service_name": "Reports Task Service"
               }
           ],
           "version": "0.7.0",
           "created_at": "2018-11-07T16:32:43.271141Z",
           "tags": [],
           "author": "daniel",
           "is_major": false
       }


.. http:post:: /releases/(kf_id)/publish

    Start publishing release of ``kf_id``.
    The release must be in the ``staged`` state.

    **Example**:

    .. http:example:: curl

       PATCH /releases/RE_EJTE6XDS/publish HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "message": "publishing"
       }


Release Notes
-------------

Release notes describe changes made in a release. They may optionally target
a specific study to allow individual studies to be annotated separately.


.. http:get:: /release-notes

    Returns a list of release notes

    :query limit: Number of results to return in a page, defaults to 10
    :query offset: How many items to offset the page by
    :query release: Filter tasks related to a given release's kf_id
    :query study: Filter tasks related to a given study's kf_id

    **Example**:

    .. http:example:: curl

       GET /release-notes?author=&study=SD_ME0WME0W HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
            "count": 1,
            "next": null,
            "previous": null,
            "results": [
                {
                    "kf_id": "RN_D1HXSBVD",
                    "description": "Probably need more cats",
                    "author": "daniel",
                    "created_at": "2018-10-25T20:06:22.936504Z",
                    "release": "http://kf-release-coord-dev.kidsfirstdrc.org/releases/RE_GD2D17A9",
                    "study": "http://kf-release-coord-dev.kidsfirstdrc.org/studies/SD_ME0WME0W"
                }
            ]
        }


.. http:get:: /release-notes/(kf_id)

    Get a specific note of ``kf_id``.


    **Example**:

    .. http:example:: curl

       GET /release-notes/RN_D1HXSBVD HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "kf_id": "RN_D1HXSBVD",
           "description": "Probably need more cats",
           "author": "daniel",
           "created_at": "2018-10-25T20:06:22.936504Z",
           "release": "http://kf-release-coord-dev.kidsfirstdrc.org/releases/RE_GD2D17A9",
           "study": "http://kf-release-coord-dev.kidsfirstdrc.org/studies/SD_ME0WME0W"
       }


.. http:post:: /release-notes

    Create a new note for a release. May optionally specify a study in the
    release.

    :<json string description: The description of changes in the release
    :<json string author: The author of the note
    :<json string release: The kf_id of the release that the note describes
    :<json string study: The kf_id of a study that the note describes


    **Example**:

    .. http:example:: curl

       POST /release-notes HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json

       {
           "description": "Probably need more cats",
           "author": "daniel",
           "release": "RE_GD2D17A9",
           "study": "SD_ME0WME0W"
       }


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
            "count": 1,
            "next": null,
            "previous": null,
            "results": [
                {
                    "kf_id": "RN_D1HXSBVD",
                    "description": "Probably need more cats",
                    "author": "daniel",
                    "created_at": "2018-10-25T20:06:22.936504Z",
                    "release": "http://kf-release-coord-dev.kidsfirstdrc.org/releases/RE_GD2D17A9",
                    "study": "http://kf-release-coord-dev.kidsfirstdrc.org/studies/SD_ME0WME0W"
                }
            ]
        }


.. http:patch:: /release-notes/(kf_id)

    Update a specific note of ``kf_id``.

    :<json string description: The description of changes in the release
    :<json string author: The author of the note
    :<json string release: The kf_id of the release that the note describes
    :<json string study: The kf_id of a study that the note describes

    **Example**:

    .. http:example:: curl

       PATCH /release-notes/RN_D1HXSBVD HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json

       {
           "description": "New description"
       }

       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "kf_id": "RN_D1HXSBVD",
           "description": "New description",
           "author": "daniel",
           "created_at": "2018-10-25T20:06:22.936504Z",
           "release": "http://kf-release-coord-dev.kidsfirstdrc.org/releases/RE_GD2D17A9",
           "study": "http://kf-release-coord-dev.kidsfirstdrc.org/studies/SD_ME0WME0W"
       }


.. http:delete:: /release-notes/(kf_id)

    Delete a release note of ``kf_id``.

    **Example**:

    .. http:example:: curl

       DELETE /release-notes/RN_D1HXSBVD HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json

       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept


Events
------

Events are created when tasks and releases change between states.
They are used to log status changes and history of releases for
debugging and notification purposes.

.. http:get:: /events

    Lists events.

    :query limit: Number of results to return in a page, defaults to 10
    :query offset: How many items to offset the page by
    :query release: Filter events related to a given release's kf_id
    :query study: Filter events related to a given study's kf_id
    :query task: Filter events related to a given task's kf_id
    :query task_service: Filter events related to a given task's kf_id

    **Example**:

    .. http:example:: curl

       GET /events?release=RE_N06RZ4VV HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "count": 1,
           "next": "null",
           "previous": null,
           "results": [
               {
                   "kf_id": "TA_YPK2CS52",
                   "event_type": "info",
                   "message": "release RE_N06RZ4VV, version 3.35.0 changed from publishing to published",
                   "release": "https://kf-release-coord.kidsfirstdrc.org/releases/RE_N06RZ4VV",
                   "task_service": null,
                   "task": null,
                   "created_at": "2019-07-30T18:03:54.308385Z"
               }
           ]
       }


.. http:post:: /events

    Creates a new event

    :<json string event_type: The type of event
    :<json string message: A message describing the event
    :<json string release: The ``kf_id`` of the releated release
    :<json string study: The ``kf_id`` of the releated release
    :<json string task: The ``kf_id`` of the releated release
    :<json string task_service: The ``kf_id`` of the releated release

    **Example**:

    .. http:example:: curl

       POST /events HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json

       {
            "event_type": "info",
            "message": "release RE_N06RZ4VV, version 3.35.0 changed from publishing to published",
            "release": "RE_N06RZ4VV"
        }


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
            "kf_id": "TA_YPK2CS52",
            "event_type": "info",
            "message": "release RE_N06RZ4VV, version 3.35.0 changed from publishing to published",
            "release": "https://kf-release-coord.kidsfirstdrc.org/releases/RE_N06RZ4VV",
            "task_service": null,
            "task": null,
            "created_at": "2019-07-30T18:03:54.308385Z"
        }


.. http:get:: /events/(kf_id)

    Gets an event of ``kf_id``.

    **Example**:

    .. http:example:: curl

       GET /events/TA_YPK2CS52 HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
            "kf_id": "TA_YPK2CS52",
            "event_type": "info",
            "message": "release RE_N06RZ4VV, version 3.35.0 changed from publishing to published",
            "release": "https://kf-release-coord.kidsfirstdrc.org/releases/RE_N06RZ4VV",
            "task_service": null,
            "task": null,
            "created_at": "2019-07-30T18:03:54.308385Z"
        }


.. http:delete:: /events/(kf_id)

    Delete an event of ``kf_id``.

    **Example**:

    .. http:example:: curl

       DELETE /events/TA_YPK2CS52 HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept


Studies
-------

Studies are mirrored from the dataservice and are immutable from the Release
Coordinator.
They are only used to relate releases together to create timelines for given
studies.


.. http:get:: /studies

    Returns a list of studies.

    :query limit: Number of results to return in a page, defaults to 10
    :query offset: How many items to offset the page by

    **Example**:

    .. http:example:: curl

       GET /studies HTTP/1.1
       Host: kf-release-coord.kidsfirstdrc.org
       Accept: application/json


       HTTP/1.1 200 OK
       Allow: GET, POST, HEAD, OPTIONS
       Content-Type: application/json
       Vary: Accept

       {
           "count": 1,
           "next": null,
           "previous": null,
           "results": [
               {
                   "kf_id": "SD_1P41Z782",
                   "name": "OpenDIPG: ICR London",
                   "version": "3.35.0",
                   "visible": true,
                   "last_pub_version": "3.35.0",
                   "last_pub_date": "2019-07-30T17:40:45.715939Z",
                   "deleted": false,
                   "created_at": "2019-07-29T14:29:07.227936Z"
               }
           ]
       }
