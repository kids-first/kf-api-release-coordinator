import json
import jwt
from mock import MagicMock, patch
from coordinator.authentication import EgoJWTStore


def test_store_token(mocker):
    """ Test that the ego store fetches jwts correctly """

    mock_ego = mocker.patch('coordinator.authentication.requests')
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with open('tests/ego_token.json') as f:
        resp = json.loads(f.read())
        mock_resp.json.return_value = resp

    mock_ego.post.return_value = mock_resp

    store = EgoJWTStore()
    token = jwt.decode(store.token, verify=False)

    assert 'aud' in token
    assert token['aud'][0] == 'release-coordinator'

    assert mock_ego.post.call_count == 1
    url = 'http://ego/oauth/token'
    data = ('grant_type=client_credentials&client_id=test-client&' +
            'client_secret=test-secret')
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    mock_ego.post.assert_called_with(url, data=data, headers=headers)

    assert store.header == {'Authorization': f"Bearer {resp['access_token']}"}
