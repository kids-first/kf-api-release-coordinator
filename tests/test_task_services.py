import pytest
from requests.exceptions import ConnectionError
from mock import Mock, patch
from coordinator.api.models import TaskService


BASE_URL = 'http://testserver'


def test_no_task_service(client, transactional_db):
    """ Test basic response """
    assert TaskService.objects.count() == 0
    resp = client.get(BASE_URL+'/task-services')
    assert resp.status_code == 200


def test_basic_task_service(client, transactional_db, task_service):
    """ Test basic response """
    assert TaskService.objects.count() == 1
    resp = client.get(BASE_URL+'/task-services')
    assert resp.status_code == 200
    res = resp.json()
    assert res['count'] == 1


def test_url_validation(client, db, task_service):
    """ Test that urls are validated by pinging their status endpoint """
    orig = TaskService.objects.count()
    with patch('coordinator.api.validators.requests') as mock_requests:
        mock_requests.get = Mock()
        mock_resp = Mock()
        mock_resp.content = ''
        mock_requests.get.return_value = mock_resp
        mock_requests.get.status_code.return_value = 404

        # Test basic url field validation
        service = {'url': 'not a url',
                   'name': 'test service',
                   'description': 'lorem ipsum'}
        resp = client.post(BASE_URL+'/task-services', data=service)
        res = resp.json()
        assert res['url'][0] == 'Enter a valid URL.'
        assert TaskService.objects.count() == orig

        # Test validation against endpoint

        service['url'] = 'http://validurl.com'
        resp = client.post(BASE_URL+'/task-services', data=service)
        res = resp.json()
        assert 'validurl.com did not return the expected /st' in res['url'][0]
        assert TaskService.objects.count() == orig

        mock_resp.status_code = 200
        mock_resp.content = '{}'
        mock_requests.get.return_value = mock_resp
        resp = client.post(BASE_URL+'/task-services', data=service)
        res = resp.json()
        assert 'validurl.com did not return the expected /st' in res['url'][0]
        assert TaskService.objects.count() == orig

        mock_resp.content = '{"name": "test"}'
        mock_requests.get.return_value = mock_resp
        resp = client.post(BASE_URL+'/task-services', data=service)
        res = resp.json()
        assert 'kf_id' in res
        assert TaskService.objects.count() == orig + 1


@pytest.mark.parametrize('field', [
    'kf_id',
    'url',
    'health_status',
    'last_ok_status',
    'created_at'
])
def test_task_service_fields(client, db, task_service, field):
    resp = client.get(BASE_URL+'/task-services')
    task_service = resp.json()['results'][0]
    assert field in task_service


def test_task_service_bad_status(client, db, task_service):
    """ Test that a non-200 response increases task's last_ok_status count """
    kf_id = task_service['kf_id']
    ts = TaskService.objects.get(kf_id=kf_id)
    with patch('coordinator.api.models.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = ConnectionError()
        mock_requests.get.return_value = mock_resp
        mock_requests.get.status_code.return_value = 404
        ts.health_check()
        assert mock_requests.get.call_count == 1
        assert ts.health_status == 'ok'
        mock_requests.get.assert_called_with('http://ts.com/status')
        assert ts.last_ok_status == 1
        ts.health_check()
        ts.health_check()
        ts.health_check()
        assert ts.last_ok_status == 4
        assert ts.health_status == 'down'
