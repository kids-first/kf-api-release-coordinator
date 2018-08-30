import pytest
from datetime import datetime, timezone
from requests.exceptions import ConnectionError
from mock import Mock, patch
from coordinator.api.models import Release, Study
from coordinator.api.serializers import StudySerializer


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


def test_nested_releases(admin_client, transactional_db, release, studies):
    """ Test that nested release resource is returned correctly """
    resp = admin_client.get(BASE_URL+'/releases')
    assert len(resp.json()['results']) == 1
    assert resp.json()['results'][0]['studies'] == ['SD_00000001']

    resp = admin_client.get(BASE_URL+'/studies/SD_00000001/releases')
    assert resp.json()['count'] == 1

    resp = admin_client.post(BASE_URL+'/releases',
                             data={'name': 'test',
                                   'studies': ['SD_00000000', 'SD_00000001']})

    resp = admin_client.get(BASE_URL+'/studies/SD_00000001/releases')
    assert resp.json()['count'] == 2
    assert resp.json()['results'][-1]['kf_id'] == release['kf_id']


def test_sync_studies_fail(client):
    """ Test that dataservice errors are returned when there is a problem  """
    with patch('coordinator.api.views.studies.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.json.return_value = {'message': 'server error'}
        mock_requests.get.return_value = mock_resp
        mock_requests.get.return_value.status_code = 500

        resp = client.post(BASE_URL+'/studies/sync')
        assert resp.status_code == 500
        res = resp.json()
        assert res['message'] == 'server error'

        assert mock_requests.get.call_count == 1
        expected = 'http://dataservice/studies?limit=100'
        mock_requests.get.assert_called_with(expected)

        mock_resp.json.return_value = {'<html>Server error</html>'}
        mock_requests.get.return_value = mock_resp
        mock_requests.get.return_value.status_code = 500

        resp = client.post(BASE_URL+'/studies/sync')
        assert resp.status_code == 500
        res = resp.json()
        assert res['message'].endswith('getting studies from the dataservice')

        assert mock_requests.get.call_count == 2
        expected = 'http://dataservice/studies?limit=100'
        mock_requests.get.assert_called_with(expected)


def test_sync_studies_updated(client, db, studies):
    """ Test that fields are updated on change in dataservice """
    with patch('coordinator.api.views.studies.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.json.return_value = {
            'results': [StudySerializer(v).data for v in studies.values()]
        }
        mock_resp.json.return_value['results'][-1]['name'] = 'Updated Name'
        mock_requests.get.return_value = mock_resp
        mock_requests.get.return_value.status_code = 200

        assert Study.objects.count() == 5

        resp = client.post(BASE_URL+'/studies/sync')
        assert resp.status_code == 200
        res = resp.json()

        assert mock_requests.get.call_count == 1
        expected = 'http://dataservice/studies?limit=100'
        mock_requests.get.assert_called_with(expected)

        assert Study.objects.count() == 5
        assert Study.objects.get(kf_id='SD_00000004').name == 'Updated Name'


def test_sync_studies_deleted(client, db, studies):
    """ Test that studies are set as deleted when removed from dataservice """
    with patch('coordinator.api.views.studies.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.json.return_value = {
            'results': [StudySerializer(v).data for v in studies.values()]
        }
        mock_resp.json.return_value['results'][-1]['name'] = 'Updated Name'
        mock_requests.get.return_value = mock_resp
        mock_requests.get.return_value.status_code = 200

        assert Study.objects.count() == 5

        resp = client.post(BASE_URL+'/studies/sync')
        assert resp.status_code == 200
        res = resp.json()

        # Remove a study
        mock_resp.json.return_value = {
            'results': mock_resp.json.return_value['results'][:-1]
        }

        resp = client.post(BASE_URL+'/studies/sync')
        assert resp.status_code == 200
        assert resp.json()['new'] == 0
        assert resp.json()['deleted'] == 1
        assert Study.objects.count() == 5

        assert Study.objects.get(kf_id='SD_00000004').deleted


def test_no_delete_update(client, db, studies):
    """ Test that studies may not be deleted or updated from api """
    resp = client.post(BASE_URL+'/studies', data={'name': 'test'})
    assert resp.status_code == 405
    assert resp.json() == {'detail': 'Method "POST" not allowed.'}

    resp = client.delete(BASE_URL+'/studies/SD_00000001')
    assert resp.status_code == 405
    assert resp.json() == {'detail': 'Method "DELETE" not allowed.'}
    assert Study.objects.count() == 5


def test_latest_version(admin_client, db, studies):
    """
    Test that the latest version field is populated when a study
    is included in a release
    """
    resp = admin_client.post(BASE_URL+'/releases',
                             data={'name': 'test',
                                   'studies': ['SD_00000000', 'SD_00000001']})
    assert resp.status_code == 201
    v1 = resp.json()['version']
    assert v1 == '0.0.0'

    resp = admin_client.get(BASE_URL+'/studies/SD_00000000')
    assert resp.json()['version'] == v1
    resp = admin_client.get(BASE_URL+'/studies/SD_00000002')
    assert resp.json()['version'] is None

    # Make another release
    resp = admin_client.post(BASE_URL+'/releases',
                             data={'name': 'test',
                                   'studies': ['SD_00000001', 'SD_00000002']})
    assert resp.status_code == 201
    v2 = resp.json()['version']
    assert v2 == '0.0.1'

    resp = admin_client.get(BASE_URL+'/studies/SD_00000000')
    assert resp.json()['version'] == v1
    resp = admin_client.get(BASE_URL+'/studies/SD_00000001')
    assert resp.json()['version'] == v2
    resp = admin_client.get(BASE_URL+'/studies/SD_00000002')
    assert resp.json()['version'] == v2


def test_new_study(client, db, studies):
    """ Test case that a new study has been added to the dataservice """
    with patch('coordinator.api.views.studies.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.json.return_value = {
            'results': [StudySerializer(v).data for v in studies.values()]
        }
        mock_resp.json.return_value['results'].append({
            'kf_id': 'SD_XXXXXXXX',
            'name': 'New Study',
            'external_id': 'New',
            'visible': True,
            'created_at': datetime(year=2019, month=6, day=6,
                                   tzinfo=timezone.utc),
        })
        mock_requests.get.return_value = mock_resp
        mock_requests.get.return_value.status_code = 200

        assert Study.objects.count() == 5

        resp = client.post(BASE_URL+'/studies/sync')
        assert resp.status_code == 200
        res = resp.json()
        assert res['new'] == 1
        assert res['deleted'] == 0

        assert mock_requests.get.call_count == 1
        expected = 'http://dataservice/studies?limit=100'
        mock_requests.get.assert_called_with(expected)

        assert Study.objects.count() == 6
        assert Study.objects.get(kf_id='SD_XXXXXXXX').name == 'New Study'


def test_get_study(client, db):
    """ Test that dataservice is called for studies """
    return
    with patch('coordinator.api.views.studies.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = ConnectionError()
        mock_resp.json.return_value = {'results': {'external_id': 'phs'}}
        mock_requests.get.return_value = mock_resp
        mock_requests.get.status_code.return_value = 404

        resp = client.get(BASE_URL+'/studies/SD_00000000')

        # assert mock_requests.get.call_count == 1
        expected = 'http://dataservice/studies/SD_00000000'
        # mock_requests.get.assert_called_with(expected)
        # assert 'external_id' in resp.json()['results']
