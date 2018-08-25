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
    """ Test that fields exist on the response """
    resp = client.get(BASE_URL+'/tasks')
    task = resp.json()['results'][0]
    assert field in task


def test_task_filters(client, db, task):
    """ Test that tasks are filterable by task service """
    # Task service filter
    ts = TaskService.objects.first()
    resp = client.get(BASE_URL+'/tasks?task_service=blah')
    count = resp.json()['count']
    assert count == 0
    resp = client.get(BASE_URL+'/tasks?task_service='+ts.kf_id)
    count = resp.json()['count']
    assert count == 1

    # Release filter
    r = Release.objects.first()
    resp = client.get(BASE_URL+'/tasks?release=blah')
    count = resp.json()['count']
    assert count == 0
    resp = client.get(BASE_URL+'/tasks?release='+r.kf_id)
    count = resp.json()['count']
    assert count == 1

    # Release and service filter
    resp = client.get(BASE_URL+'/tasks?release=blah&task_service=blah')
    count = resp.json()['count']
    assert count == 0
    url = BASE_URL+f'/tasks?release={r.kf_id}&task_service={ts.kf_id}'
    resp = client.get(url)
    count = resp.json()['count']
    assert count == 1


def test_task_relations(client, transactional_db, task):
    """ Test basic response """
    assert Release.objects.count() == 1
    assert TaskService.objects.count() == 1
    assert Task.objects.count() == 1

    release = task['release']
    task_service = task['task_service']

    assert task['release'].endswith(Release.objects.first().kf_id)
    assert task['task_service'].endswith(TaskService.objects.first().kf_id)


def test_status_check(client, transactional_db, task, worker):
    """ Check that task status are updated correctly """
    t = Task.objects.get(kf_id=task['kf_id'])
    with patch('coordinator.api.models.task.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.json.return_value = {
            'task_id': t.kf_id,
            'release_id': t.release.kf_id,
            'state': 'failed',
            'progress': 100
        }
        mock_requests.post.return_value = mock_resp
        t.status_check()
        assert mock_requests.post.call_count == 1
        assert t.state == 'failed'
        expected = {
            'task_id': t.kf_id,
            'release_id': t.release.kf_id,
            'action': 'get_status'
        }
        mock_requests.post.assert_called_with('http://ts.com/tasks',
                                              timeout=15,
                                              json=expected)

        worker.work(burst=True)
        release = t.release
        assert release.state == 'canceling'
