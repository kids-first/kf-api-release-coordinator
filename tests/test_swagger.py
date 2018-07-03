import pytest


@pytest.mark.parametrize('endpoint', [
    '/swagger.json',
    '/swagger.yaml',
    '/swagger/',
    '/redoc/'])
def test_endpoints(client, endpoint, db):
    """ Test the different swagger endpoints """
    resp = client.get(endpoint)
    assert resp.status_code == 200


def test_version(client, db):
    resp = client.get('/swagger.json')
    assert resp.json()['info']['version'].count('.') == 2
