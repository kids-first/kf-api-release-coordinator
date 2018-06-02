import jwt
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

        return (user, None)
