import uuid
import requests
from requests.exceptions import RequestException 

from django.db import models
from coordinator.utils import kf_id_generator
from coordinator.api.validators import validate_endpoint


def task_service_id():
    return kf_id_generator('TS')()


class TaskService(models.Model):
    """
    A Task Service runs a particular Task that is required for a release

    :param kf_id: The Kids First identifier, 'TS' prefix
    :param uuid: A uuid assigned to the task service for identification
    :param name: The name of the task service
    :param description: Description of the task service's function
    :param url: The root url of the task service api
    :param author: The creator of the service
    :param last_ok_status: The number of pings since the last 200 response
        from the /status endpoint on the task service
    :param health_status: The status of the service. 'ok' if one of the last
        3 pings to the /status endpoint returned 200, 'down' otherwise
    :param enabled: Only enabled tasks will be run in a release
    :param created_at: The time that the task service was registered with the
        coordinator.
    """
    kf_id = models.CharField(max_length=11, primary_key=True,
                             default=task_service_id,
                             help_text='Kids First ID assigned to the service')
    uuid = models.UUIDField(default=uuid.uuid4,
                            help_text='UUID used internally')
    name = models.CharField(max_length=100,
                            help_text='The name of the service')
    description = models.CharField(max_length=500,
                                   help_text='Description of the service\'s'
                                   'function')
    url = models.CharField(max_length=200, validators=[validate_endpoint],
                           help_text='endpoint for the task\'s API')
    author = models.CharField(max_length=100, blank=False,
                              help_text='The user who created the service')
    last_ok_status = models.IntegerField(default=0,
                                         help_text='number of pings since last'
                                         ' 200 response from the task\'s '
                                         ' /status endpoint')
    enabled = models.BooleanField(default=True,
                                  help_text='Whether to run the task as part '
                                  'of a release.')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Time the task was created')

    @property
    def health_status(self):
        return 'ok' if self.last_ok_status <= 3 else 'down'

    def health_check(self):
        """
        Ping the TaskService /status endpoint to check that the service is
        healthy.
        """
        try:
            resp = requests.get(self.url+'/status', timeout=15)
            resp.raise_for_status()
        except RequestException:
            self.last_ok_status += 1
            self.save()
            return

        if self.last_ok_status > 0:
            self.last_ok_status = 0
            self.save()
