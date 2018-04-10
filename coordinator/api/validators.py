from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_study(study):
    """ Check that a list of kf_ids for studies is given """
    if len(study) != 11 or study[:3] != 'SD_':
        raise ValidationError(
            _('%(value)s is not a valid study kf_id'),
            params={'value': study},
        )
