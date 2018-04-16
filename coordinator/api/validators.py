import requests
from requests.exceptions import ConnectionError
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
    URLValidator()(url)
    resp = None
    fail = False
    try:
        resp = requests.get(url+'/status')
    except ConnectionError:
        fail = True

    if (resp and (
            resp.status_code != 200 or
            'name' not in resp.content)):
        fail = True

    if fail:
        raise ValidationError(
            _('%(value)s did not return the expected /status response'),
            params={'value': url},
        )
