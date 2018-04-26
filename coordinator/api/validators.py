import requests
from requests.exceptions import ConnectionError, HTTPError
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_study(study):
    """ Check that a list of kf_ids for studies is given """
    if len(study) != 11 or study[:3] != 'SD_':
        raise ValidationError(
            _('%(value)s is not a valid study kf_id'),
            params={'value': study},
        )


def validate_endpoint(url):
    """ Check that a url provided as an endpoint has expected format """
    # URLValidator()(url)
    if not (url.startswith('http')):
        raise ValidationError(
            _('Enter a valid URL.')
        )

    try:
        resp = requests.get(url+'/status')
        resp.raise_for_status()
        assert 'name' in resp.content.decode()
    except (ConnectionError, HTTPError, AssertionError):
        raise ValidationError(
            _('%(value)s did not return the expected /status response'),
            params={'value': url},
        )
