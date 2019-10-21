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


def headers():
    """ Construct headers for requests to task services """
    headers = {
        "Authorization": "Bearer "
        + cache.get_or_set(
            settings.CACHE_AUTH0_SERVICE_KEY,
            get_service_token,
            settings.CACHE_AUTH0_TIMEOUT,
        )
    }
    headers.update(settings.REQUESTS_HEADERS)
    return headers


def get_service_token():
    """ Get a new token from Auth0 """
    url = f"{settings.AUTH0_DOMAIN}/oauth/token"
    headers = {"Content-Type": "application/json"}
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.AUTH0_CLIENT,
        "client_secret": settings.AUTH0_SECRET,
        "audience": settings.AUTH0_AUD,
    }

    try:
        resp = requests.post(
            url, headers=headers, json=data, timeout=settings.REQUEST_TIMEOUT
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        logger.error(f"Problem retrieving access token from Auth0: {err}")

    content = resp.json()

    if "access_token" not in content:
        logger.error(f"Access token response malformed: {resp.content}")
        return

    token = content["access_token"]
    return token
