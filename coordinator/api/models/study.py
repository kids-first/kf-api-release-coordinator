import datetime
import uuid
import requests
from requests.exceptions import ConnectionError, HTTPError

import django_rq
from django.db import models
from django_fsm import FSMField, transition

from coordinator.utils import kf_id_generator


class Study(models.Model):
    """
    A study from the dataservice.
    Only store the kf_id and the name of the study.

    :param kf_id: The Kids First identifier, 'SD' prefix
    :param name: The name of the study
    :param created_at: The time that the task was registered with the
        coordinator.
    """
    kf_id = models.CharField(max_length=11, primary_key=True,
                             null=False)
    name  = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=False,
                                      null=True,
                                      help_text='Time the task was created')
