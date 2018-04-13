import importlib
import pytest
from django.conf import settings


BASE_URL = 'http://testserver'
URLS = [
    '/releases',
    '/task-services',
    '/tasks',
]


@pytest.fixture
def fakes(client):
    r = client.post(BASE_URL+'/releases',
                    {'name': 'TEST', 'studies': 'SD_00000001'})
