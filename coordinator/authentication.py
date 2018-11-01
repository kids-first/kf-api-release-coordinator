import datetime
import jwt
import requests
import logging
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EgoAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        """
        Attempt to authenticate if there is an `Authorization` header
        with a token is prefixed with `Bearer `.

        :returns: The JWT context if a valid JWT was in the header,
            None otherwise.
        :raises: AuthenticationFailed if the token is not valid
        """
        if settings.DEBUG:
            return ({'roles': 'ADMIN'}, None)

        token = request.META.get('HTTP_AUTHORIZATION')
        if token is None:
            header = request.META.get('headers')
            # No headers
            if header is None:
                return ({}, None)
            token = header.get('Authorization', None)
        # No Authorization header
        if token is None:
            return ({}, None)
        # Unexpected token type
        if 'Bearer ' not in token:
            return ({}, None)

        try:
            token = token.split('Bearer ')[-1]
            decoded = jwt.decode(token, verify=False)
            context = decoded['context']
            user = context['user']
        except (KeyError, jwt.exceptions.DecodeError):
            raise exceptions.AuthenticationFailed('Not a valid JWT')

        # Check that this is a valid JWT from ego
        verify_url = settings.EGO_API + '/oauth/token/verify'
        resp = requests.get(verify_url, headers={'token': token})
        if resp.status_code != 200 or resp.json() is False:
            raise exceptions.AuthenticationFailed('Auth service unavailable')

        return (user, None)


class EgoJWTStore():
    """
    Stores the coordinator's application JWT to be sent to verify the
    coordinator's identity.
    """

    def __init__(self):
        self.expiration = 0
        self._token = None

    @property
    def token(self):

        # Check if we've fetched a token yet
        if self._token is None:
            self.get_new_token()

        # Check if we need to get a fresh token
        if datetime.datetime.utcnow().timestamp() > self.expiration - 60:
            self.get_new_token()

        return self._token

    @property
    def header(self):
        """ Automatically formats an authorization header for a request """
        return {
            'Authorization': f'Bearer {self.token}'
        }

    def get_new_token(self):
        """ Get a new token from ego """
        url = f'{settings.EGO_API}/oauth/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = (f"grant_type=client_credentials&" +
                f"client_id={settings.EGO['default']['CLIENT_ID']}&" +
                f"client_secret={settings.EGO['default']['SECRET']}")
        resp = requests.post(url, headers=headers, data=data)

        if resp.status_code != 200:
            logger.error(f'Problem retrieving JWT from ego: {resp.content}')
            return

        content = resp.json()
        if 'access_token' not in content or 'expires_in' not in content:
            logger.error(f'Ego token response malformed: {resp.content}')
            return


        self._token = content['access_token']
        self.expiration = (datetime.datetime.utcnow().timestamp()
                           + content['expires_in'])
        return self._token
