import datetime
import jwt
import json
import re
import textwrap
import requests
import logging
from django.conf import settings
from django.core.cache import cache
from rest_framework import authentication
from rest_framework import exceptions


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EgoAuthentication(authentication.BaseAuthentication):

    @staticmethod
    def _get_ego_key():
        """
        Attempts to retrieve the ego public key from the cache. If it's not
        there or is expired, fetch a new one from ego and store it back in the
        cache.
        """
        key = cache.get(settings.CACHE_EGO_KEY, None)
        # If key is not set in cache (or has timed out), get a new one
        if key is None:
            key = EgoAuthentication._get_new_key()
            cache.set(settings.CACHE_EGO_KEY, key, settings.CACHE_EGO_TIMEOUT)
        return key

    @staticmethod
    def _get_new_key():
        """
        Get a public key from ego
        We reformat the keystring as the whitespace is not always consistent
        with the pem format
        """
        resp = requests.get(f'{settings.EGO_API}/oauth/token/public_key',
                            timeout=10)
        key = resp.content
        key = key.replace(b'\n', b'')
        key = key.replace(b'\r', b'')
        key_re = r'-----BEGIN PUBLIC KEY-----(.*)-----END PUBLIC KEY-----'
        contents = re.match(key_re, key.decode('utf-8')).group(1)
        contents = '\n'.join(textwrap.wrap(contents, width=65))
        contents = f'\n{contents}\n'
        key = f'-----BEGIN PUBLIC KEY-----{contents}-----END PUBLIC KEY-----'
        key = key.encode()
        return key

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
                return None
            token = header.get('Authorization', None)
        # No Authorization header
        if token is None:
            return None
        # Unexpected token type
        if 'Bearer ' not in token:
            return None

        token = token.split('Bearer ')[-1]

        try:
            # Validate JWT using Ego's public key
            public_key = EgoAuthentication._get_ego_key()
            token = jwt.decode(token, public_key, algorithms='RS256',
                               options={'verify_aud': False})
        except jwt.exceptions.DecodeError as err:
            logger.error(f'Problem authenticating request: {err}')
            return None
        except jwt.exceptions.InvalidTokenError as err:
            logger.error(f'Token provided is not valid: {err}')
            return None

        user = token['context']['user']

        return (user, None)


class Auth0Authentication(authentication.BaseAuthentication):

    @staticmethod
    def _get_auth0_key():
        """
        Attempts to retrieve the ego public key from the cache. If it's not
        there or is expired, fetch a new one from ego and store it back in the
        cache.
        """
        key = cache.get(settings.CACHE_AUTH0_KEY, None)
        # If key is not set in cache (or has timed out), get a new one
        if key is None:
            key = Auth0Authentication._get_key()
            cache.set(settings.CACHE_AUTH0_KEY, key,
                      settings.CACHE_AUTH0_TIMEOUT)
        return key

    @staticmethod
    def _get_new_key():
        """
        Get a public key from Auth0's JWKS
        Reformat the JWKS into a PEM format
        """
        resp = requests.get(settings.AUTH0_JWKS, timeout=10)
        key = resp.json()['keys'][0]
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        return public_key

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
                return None
            token = header.get('Authorization', None)
        # No Authorization header
        if token is None:
            return None
        # Unexpected token type
        if 'Bearer ' not in token:
            return None

        token = token.split('Bearer ')[-1]

        try:
            public_key = Auth0Authentication._get_new_key()
            token = jwt.decode(token, public_key, algorithms='RS256',
                               options={'verify_aud': False})
        except (TypeError, KeyError):
            # If we had trouble getting JWKS
            return None
        except jwt.exceptions.DecodeError as err:
            logger.error(f'Problem authenticating request: {err}')
            return None
        except jwt.exceptions.InvalidTokenError as err:
            logger.error(f'Token provided is not valid: {err}')
            return None

        token['permissions'] = token['https://kidsfirstdrc.org/permissions']
        token['groups'] = token['https://kidsfirstdrc.org/groups']
        token['roles'] = token['https://kidsfirstdrc.org/roles']
        del token['https://kidsfirstdrc.org/permissions']
        del token['https://kidsfirstdrc.org/groups']
        del token['https://kidsfirstdrc.org/roles']

        return (token, None)


def get_service_token():
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

    token = content['access_token']
    header = {'Authorization': 'Bearer '+token}
    return header
