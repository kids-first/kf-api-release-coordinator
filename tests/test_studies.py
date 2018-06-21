import pytest
from requests.exceptions import ConnectionError
from mock import Mock, patch
from coordinator.api.models import TaskService, Task


BASE_URL = 'http://testserver'


def test_get_studies(client, db):
    """ Test that dataservice is called for studies """
    with patch('coordinator.api.views.studies.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = ConnectionError()
        mock_resp.json.return_value = {'results': []}
        mock_requests.get.return_value = mock_resp
        mock_requests.get.status_code.return_value = 404

        client.get(BASE_URL+'/studies')

        assert mock_requests.get.call_count == 1
        expected = 'http://dataservice/studies?limit=100'
        mock_requests.get.assert_called_with(expected)


def test_get_study(client, db):
    """ Test that dataservice is called for studies """
    with patch('coordinator.api.views.studies.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = ConnectionError()
        mock_resp.json.return_value = {'results': {'external_id': 'phs'}}
        mock_requests.get.return_value = mock_resp
        mock_requests.get.status_code.return_value = 404

        resp = client.get(BASE_URL+'/studies/SD_00000000')

        assert mock_requests.get.call_count == 1
        expected = 'http://dataservice/studies/SD_00000000'
        mock_requests.get.assert_called_with(expected)
        assert 'external_id' in resp.json()['results']
