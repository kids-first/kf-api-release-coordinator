import os
import json
import pytest
import mock
import requests
from coordinator.api.models import Release, Study, Task, TaskService, Event


def test_fail_cancel(admin_client, dev_client, client, transactional_db,
                     mocker, worker, task_service, study):
    """
    Test that when a cancel_release task fails and the release not set to
    a terminal state (canceled, failed), then the status_checks on the
    releases's tasks are unable to re-invoke the cancel_release task because
    they hit an unallowed transition before trying to enqueue the task
    """
    # Our task should respond 'failed' during status check, even though
    # it is 'running' internally
    mock_task_requests = mocker.patch('coordinator.api.models.task.requests')
    mock_task_action = mock.Mock()
    mock_task_action.status_code = 200
    mock_task_action.json.return_value = {'state': 'failed'}
    mock_task_requests.post.return_value = mock_task_action

    # Our release is in the 'canceling' state and `cancel_release` task is
    # yet to be called
    release = Release(name='test', tags=[])
    release.state = 'canceling'
    release.save()
    task = Task('TA_00000000',
                release=release,
                task_service=TaskService.objects.first(),
                state='running')
    task.save()
    # The status check should call the `cancel_release` task to update the
    # release state and the task state to failed
    task.status_check()

    assert release.state == 'canceling'

    worker.work(burst=True)

    release = Release.objects.get(kf_id=task.release_id)

    assert task.state == 'failed'
    assert release.state == 'failed'
