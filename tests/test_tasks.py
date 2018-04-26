import pytest
from mock import Mock, patch
from coordinator.api.models import Release, Task, TaskService


BASE_URL = 'http://testserver'


def test_no_task(client, transactional_db):
    """ Test basic response """
    assert Task.objects.count() == 0
    resp = client.get(BASE_URL+'/tasks')
    assert resp.status_code == 200


def test_basic_task(client, transactional_db, task):
    """ Test basic response """
    assert Task.objects.count() == 1
    resp = client.get(BASE_URL+'/tasks')
    assert resp.status_code == 200
    res = resp.json()
    assert res['count'] == 1


@pytest.mark.parametrize('field', [
    'kf_id',
    'state',
    'progress',
    'release',
    'task_service',
    'created_at',
    'service_name'
])
def test_task_fields(client, db, task, field):
    resp = client.get(BASE_URL+'/tasks')
    task = resp.json()['results'][0]
    assert field in task


def test_task_relations(client, transactional_db, task):
    """ Test basic response """
    assert Release.objects.count() == 1
    assert TaskService.objects.count() == 1
    assert Task.objects.count() == 1

    release = task['release']
    task_service = task['task_service']

    assert task['release'].endswith(Release.objects.first().kf_id)
    assert task['task_service'].endswith(TaskService.objects.first().kf_id)
