import os
import jwt
import pytest
from mock import Mock, patch
from django.conf import settings


BASE_URL = 'http://testserver'


def test_invalid_jwt(client, db, fakes):
    """
    Any endpoint will try to authenticate if there is an Authorization
    header that is prefixed with `Bearer `.
    Test that a poorly formatted token fails validation
    """
    resp = client.post(BASE_URL+'/releases',
                       data={'name': 'test', 'studies': ['SD_00000000']},
                       headers={'Authorization': 'Bearer INVALID'})

    assert resp.status_code == 403
    assert resp.json()['detail'].startswith('Authentication credentials were')


def test_invalid_jwt_signature(client, db, token):
    """
    Any endpoint will try to authenticate if there is an Authorization
    header that is prefixed with `Bearer `.
    Test that an improperly signed token fails validation
    """
    decoded = jwt.decode(token(), verify=False)
    with open('tests/keys/other_private_key.pem') as f:
        key = f.read()
    encoded = jwt.encode(decoded, key, algorithm='RS256').decode('utf-8')

    resp = client.post(BASE_URL+'/releases',
                       data={'name': 'test', 'studies': ['SD_00000000']},
                       headers={'Authorization': f'Bearer {str(encoded)}'})

    assert resp.status_code == 403
    assert resp.json()['detail'].startswith('Authentication credentials were')


def test_my_studies(user_client, db, fakes):
    """
    Test that the user may create a release involving their studies
    """
    resp = user_client.post(
        BASE_URL+'/releases',
        data={'name': 'test', 'studies': ['SD_00000001'], 'tags': []}
    )

    assert resp.status_code == 201


def test_not_my_study(user_client, db, fakes):
    """
    Test that user is not allowed to release a study they do not own
    """
    resp = user_client.post(
        BASE_URL+'/releases',
        data={'name': 'test', 'studies': ['SD_XXXXXXXX']}
    )

    assert resp.json()['detail'] == 'Not allowed'
    assert resp.status_code == 403


@pytest.mark.parametrize('user_type,response_code', [
        ('admin_user', 201),
        ('dev_user', 201),
        ('user', 403),
        ('unauthed_user', 403)
])
def test_new_service(client, db, fakes, mocker, user_headers, user_type,
                     response_code):
    """
    Test that only devs and admin can make services
    """
    headers = user_headers(user_type)

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
                       headers=headers)
    assert resp.status_code == response_code


def test_invalid_token(user_client, db, fakes, mocker):
    """
    Test that the api rejects permission when token cannot be validated by ego
    """
    mock_auth_requests = mocker.patch('coordinator.authentication.requests')
    mock_auth_resp = Mock()
    mock_auth_resp.status_code = 200
    mock_auth_resp.json.return_value = False
    mock_auth_requests.get.return_value = mock_auth_resp

    resp = user_client.post(
        BASE_URL+'/task-services',
        data={'name': 'test',
              'description': 'my service',
              'author': 'daniel@d3b.center',
              'url': BASE_URL}
    )

    assert resp.status_code == 403
    assert resp.json()['detail'] == 'Must be a developer'


@pytest.mark.parametrize('user_type,response_code', [
        ('admin_user', 200),
        ('dev_user', 200),
        ('user', 200),
        ('unauthed_user', 200)
])
def test_health_checks(client, db, fakes, user_headers, user_type,
                       response_code):
    """
    Test that all users may post to /heath-checks
    """
    headers = user_headers(user_type)
    resp = client.post(BASE_URL+'/task-services/health_checks',
                       headers=headers)
    assert resp.status_code == response_code
