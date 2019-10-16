import logging
import json
import jwt
import requests
from dataclasses import dataclass, field
from typing import List
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import update_last_login


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class User:
    username: str
    email: str
    first_name: str
    last_name: str
    sub: str
    groups: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True


class Auth0AuthenticationMiddleware:
    """
    Authentication middleware for validating a user's identity through Auth0
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only attempt to resolve if user has not yet been extracted
        if not request.user.is_authenticated:
            request.user = self.__class__.get_jwt_user(request)
        return self.get_response(request)

    @staticmethod
    def get_jwt_user(request):
        """
        Creates a user object from the JWT in the Authorization header.
        This user object will be used to grant permissions based on their
        groups and roles.
        If no valid token is found, an anonymous user will be returned

        If running with the DEBUG = True setting, all requests will be
        treated as requests from an admin to grant permission to all data
        """
        if settings.DEBUG:
            # Assume user is admin if running in dev mode
            return User(
                username="devadmin",
                roles=["ADMIN"],
                email="admin@kidsfirstdrc.org",
                first_name="dev",
                last_name="admin",
                sub="123",
            )

        user = request.user
        if user.is_authenticated:
            return user

        encoded = request.META.get("HTTP_AUTHORIZATION")
        # No Authorization header
        if encoded is None:
            encoded = request.META.get('headers')
            if encoded is None:
                return None
            encoded = encoded.get('Authorization')
            if encoded is None:
                return None
        # Unexpected token type
        if "Bearer " not in encoded:
            return None

        encoded = encoded.split("Bearer ")[-1]
        token = None

        try:
            # Validate JWT using the Auth0 key
            public_key = Auth0AuthenticationMiddleware._get_auth0_key()
            token = jwt.decode(
                encoded,
                public_key,
                algorithms="RS256",
                # audience=settings.AUTH0_AUD,
                options={"verify_aud": False},
            )
        except jwt.exceptions.DecodeError as err:
            logger.error(f"Problem authenticating request from Auth0: {err}")
            return AnonymousUser()
        except jwt.exceptions.InvalidTokenError as err:
            logger.error(f"Token provided is not valid for Auth0: {err}")
            return AnonymousUser()

        sub = token.get("sub")
        groups = token.get("https://kidsfirstdrc.org/groups")
        roles = token.get("https://kidsfirstdrc.org/roles")
        # Currently unused
        permissions = token.get("https://kidsfirstdrc.org/permissions")

        # If the token is a service token and has the right scope, we will
        # auth it as equivelant to an admin user
        if token.get("gty") == "client-credentials":
            user = User(roles=["ADMIN"])
            # We will return the service user here without trying to save it
            # to the database.
            return user

        # Try to resolve ego fields
        if groups is None or roles is None or sub is None:
            context = token.get("context", {}).get("user", {})
            groups = context.get("groups")
            roles = context.get("roles")
            # Currently unused
            permissions = context.get("permissions")

            if groups is None or roles is None or sub is None:
                return AnonymousUser()

        profile = Auth0AuthenticationMiddleware._get_profile(encoded)

        # Problem getting the profile, don't try to create the user now
        if profile is None:
            user = User(groups=groups, roles=roles)
            return user
        user = User(
            username=profile.get("nickname", ""),
            email=profile.get("email", ""),
            first_name=profile.get("given_name", ""),
            last_name=profile.get("family_name", ""),
            groups=groups,
            roles=roles,
            sub=token.get("sub"),
        )

        return user

    def _get_profile(encoded):
        """
        Retrives user's profile from Auth0 to populate fields such as email

        :param token: The verified access token from the request
        """
        try:
            resp = requests.get(
                f"{settings.AUTH0_DOMAIN}/userinfo",
                headers={"Authorization": "Bearer " + encoded},
                timeout=5,
            )
        except requests.ConnectionError as err:
            logger.error(f"Problem fetching user profile from Auth0: {err}")
            return None
        return resp.json()

    @staticmethod
    def _get_auth0_key():
        """
        Attempts to retrieve the auth0 public key from the cache. If it's not
        there or is expired, fetch a new one from auth0 and store it back in
        the cache.
        """
        key = cache.get(settings.CACHE_AUTH0_KEY, None)
        # If key is not set in cache (or has timed out), get a new one
        if key is None:
            key = Auth0AuthenticationMiddleware._get_new_key()
            cache.set(
                settings.CACHE_AUTH0_KEY, key, settings.CACHE_AUTH0_TIMEOUT
            )
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        return public_key

    @staticmethod
    def _get_new_key():
        """
        Get a public key from Auth0 jwks
        """
        resp = requests.get(settings.AUTH0_JWKS, timeout=10)
        return resp.json()["keys"][0]
