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


User = get_user_model()


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
                auth_roles=["ADMIN"],
                auth_groups=[],
                email="admin@kidsfirstdrc.org",
                first_name="dev",
                last_name="admin",
                sub="123",
            )

        user = request.user
        if user.is_authenticated:
            return user

        encoded = request.META.get("HTTP_AUTHORIZATION")
        if encoded is None and "headers" in request.META:
            encoded = request.META["headers"].get("Authorization")

        if not encoded or not encoded.startswith("Bearer "):
            return AnonymousUser()
        encoded = encoded.replace("Bearer ", "")

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
            user = User()
            user.auth_roles = ["ADMIN"]
            user.auth_groups = []
            # We will return the service user here without trying to save it
            # to the database.
            return user

        if groups is None or roles is None or sub is None:
            return AnonymousUser()

        # Now we know that the token is valid so we will try to see if the user
        # is in our database yet, if so, we will return that user, if not, we
        # will create a new user by fetching more information from auth0 and
        # saving it in the database
        try:
            user = User.objects.get(sub=token["sub"])
            # The user is already in the database, update their last login
            update_last_login(None, user)
        except User.DoesNotExist:
            profile = Auth0AuthenticationMiddleware._get_profile(encoded)
            # Problem getting the profile, don't try to create the user now
            if profile is None:
                user = User(auth_groups=groups, auth_roles=roles)
                return user
            user = User(
                username=profile.get("nickname", ""),
                email=profile.get("email", ""),
                first_name=profile.get("given_name", ""),
                last_name=profile.get("family_name", ""),
                picture=profile.get("picture", ""),
                auth_groups=[],
                auth_roles=[],
                sub=token.get("sub"),
            )
            user.save()
            update_last_login(None, user)

        # NB: We ALWAYS use the JWT as the source of truth for authorization
        # fields. They will always be stored as empty arrays in the database
        # and populated on every request from the token after validation.
        user.auth_groups = groups
        user.auth_roles = roles

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
