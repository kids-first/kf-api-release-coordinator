import pytest
from requests.exceptions import ConnectionError
from mock import Mock, patch
from coordinator.api.models import Release, Study


BASE_URL = 'http://testserver'


def test_many_to_many_model(transactional_db, studies):
    """ Test creating many releases with many studies """
    r1 = Release(name='Release 1')
    r1.save()
    r1.studies.set([studies['SD_00000001'], studies['SD_00000002']])
    r1.save()

    # Inspect from the release side
    assert Release.objects.count() == 1
    assert len(Release.objects.first().studies.all()) == 2

    # Inspect from the study side
    assert Study.objects.get(kf_id='SD_00000001').release_set.first() == r1

    # Now make a new release
    r2 = Release(name='Release 2')
    r2.save()
    r2.studies.set([studies['SD_00000000'], studies['SD_00000001']])
    r2.save()

    # Inspect from the release side
    assert Release.objects.count() == 2
    r = Release.objects.get(kf_id=r2.kf_id)
    assert len(Release.objects.first().studies.all()) == 2

    # Inspect from the study side
    assert Study.objects.get(kf_id='SD_00000001').release_set.count() == 2
    assert Study.objects.get(kf_id='SD_00000000').release_set.count() == 1
    assert Study.objects.get(kf_id='SD_00000002').release_set.count() == 1


def test_many_to_many_endpoint(client, transactional_db, studies):
    release = {
        'name': 'test release',
        'studies': ['SD_00000001']
    }
    client.post(BASE_URL+'/releases')


def test_sync_studies(client, db):
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
