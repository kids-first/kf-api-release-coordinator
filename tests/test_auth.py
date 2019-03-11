import os
import pytest
from mock import Mock, patch
from django.conf import settings


BASE_URL = 'http://testserver'

with open(os.path.join(os.path.dirname(__file__), 'admin_token.txt')) as f:
    ADMIN_TOKEN = f.read().strip()
with open(os.path.join(os.path.dirname(__file__), 'dev_token.txt')) as f:
    DEV_TOKEN = f.read().strip()
with open(os.path.join(os.path.dirname(__file__), 'user_token.txt')) as f:
    USER_TOKEN = f.read().strip()


def test_invalid_jwt(client, db, fakes):
    """
    Any endpoint will try to authenticate if there is an Authorization
    header that is prefixed with `Bearer `. Test that invalid token
    results in 403
    """
    resp = client.post(BASE_URL+'/releases',
                       data={'name': 'test', 'studies': ['SD_00000000']},
                       headers={'Authorization': 'Bearer INVALID'})

    assert resp.status_code == 403
    assert resp.json()['detail'] == 'Not a valid JWT'


def test_my_studies(client, db, fakes):
    """
    Test that the user may create a release involving their studies
    """
    resp = client.post(BASE_URL+'/releases',
                       data={'name': 'test',
                             'studies': ['SD_00000000'],
                             'tags': []},
                       headers={'Authorization': 'Bearer '+USER_TOKEN})

    assert resp.status_code == 201


def test_not_my_study(client, db, fakes):
    """
    Test that user is not allowed to release a study they do not own
    """
    resp = client.post(BASE_URL+'/releases',
                       data={'name': 'test', 'studies': ['SD_XXXXXXXX']},
                       headers={'Authorization': 'Bearer '+USER_TOKEN})

    assert resp.json()['detail'] == 'Not allowed'
    assert resp.status_code == 403


@pytest.mark.parametrize('token,response_code', [
        (ADMIN_TOKEN, 201),
        (DEV_TOKEN, 201),
        (USER_TOKEN, 403)
    ])
def test_new_service(client, db, fakes, mocker, token, response_code):
    """
    Test that only devs and admin can make services
    """
    mock_service_requests = mocker.patch('coordinator.api.validators.requests')
    mock_service_resp = Mock()
    mock_service_resp.status_code = 200
    mock_service_resp.content = str.encode('{"name": "test"}')
    mock_service_requests.get.return_value = mock_service_resp

    resp = client.post(BASE_URL+'/task-services',
                       data={'name': 'test',
                             'description': 'my service',
                             'author': 'daniel@d3b.center',
                             'url': BASE_URL},
                       headers={'Authorization': 'Bearer '+token})

    assert resp.status_code == response_code


def test_invalid_token(client, db, fakes, mocker):
    """
    Test that the api rejects permission when token cannot be validated by ego
    """
    mock_auth_requests = mocker.patch('coordinator.authentication.requests')
    mock_auth_resp = Mock()
    mock_auth_resp.status_code = 200
    mock_auth_resp.json.return_value = False
    mock_auth_requests.get.return_value = mock_auth_resp

    resp = client.post(BASE_URL+'/task-services',
                       data={'name': 'test',
                             'description': 'my service',
                             'author': 'daniel@d3b.center',
                             'url': BASE_URL},
                       headers={'Authorization': 'Bearer '+USER_TOKEN})

    assert resp.status_code == 403
    assert resp.json()['detail'] == 'Auth service unavailable'


@pytest.mark.parametrize('token,response_code', [
        (ADMIN_TOKEN, 200),
        (DEV_TOKEN, 200),
        (USER_TOKEN, 200)
    ])
def test_health_checks(client, db, fakes, token, response_code):
    """
    Test that all users may post to /heath-checks
    """
    resp = client.post(BASE_URL+'/task-services/health_checks',
                       headers={'Authorization': 'Bearer '+token})
    assert resp.status_code == response_code
