import jwt
import requests
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions


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
