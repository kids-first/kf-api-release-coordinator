import uuid
import datetime
import requests

from django.db import models
from django.contrib.postgres.fields import ArrayField

from coordinator.utils import kf_id_generator
from coordinator.api.validators import validate_endpoint


STATES = [
    ('pending', 'pending'),
    ('waiting', 'waiting'),
    ('running', 'running'),
    ('staged', 'staged'),
    ('publishing', 'publishing'),
    ('published', 'published'),
    ('failed', 'failed'),
    ('canceled', 'canceled')
]

STATUSES = [
    ('green', 'green'),
    ('yellow', 'yellow'),
    ('red', 'red')
]


def task_id():
    return kf_id_generator('TA')()


def task_service_id():
    return kf_id_generator('TS')()


def release_id():
    return kf_id_generator('RE')()


class TaskService(models.Model):
    """
    A Task Service runs a particular Task that is required for a release

    :param kf_id: The Kids First identifier, 'TS' prefix
    :param uuid: A uuid assigned to the task service for identification
    :param name: The name of the task service
    :param description: Description of the task service's function
    :param url: The root url of the task service api
    :param last_ok_status: The number of pings since the last 200 response
        from the /status endpoint on the task service
    :param health_status: The status of the service. 'ok' if one of the last
        3 pings to the /status endpoint returned 200, 'down' otherwise
    :created_at: The time that the task service was registered with the
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
    url = models.URLField(validators=[validate_endpoint],
                          help_text='endpoint for the task\'s API')
    last_ok_status = models.IntegerField(default=0,
                                         help_text='number of pings since last'
                                         ' 200 response from the task\'s '
                                         ' /status endpoint')
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
        resp = requests.get(self.url+'/status')
        if resp.status_code != 200:
            self.last_ok_status += 1
            self.save()
        elif self.last_ok_status > 0:
            self.last_ok_status = 0
            self.save()


class Release(models.Model):
    """
    A Release is composed of several tasks that run process that prepare and
    publish data for a release
    """
    kf_id = models.CharField(max_length=11, primary_key=True,
                             default=release_id,
                             help_text='Kids First ID assigned to the'
                             ' release')
    uuid = models.UUIDField(default=uuid.uuid4,
                            help_text='UUID used internally')
    author = models.CharField(max_length=100, blank=False, default='admin',
                              help_text='The user who created the release')
    name = models.CharField(max_length=100,
                            help_text='Name of the release')
    description = models.CharField(max_length=500, blank=True,
                                   help_text='Release notes')
    state = models.CharField(max_length=100, choices=STATES, default='waiting',
                             help_text='The current state of the release')
    tags = ArrayField(models.CharField(max_length=50, blank=True),
                      blank=True, default=[],
                      help_text='Tags to group the release by')
    studies = ArrayField(models.CharField(max_length=11, blank=False),
                         help_text='kf_ids of the studies in this release')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Date created')


class Task(models.Model):
    """
    A Task is a process that is run on a Task Service as part of a Release

    :param kf_id: The Kids First identifier, 'TA' prefix
    :param uuid: A uuid assigned to the task for identification
    :param state: The state of the task
    :param created_at: The time that the task was registered with the
        coordinator.
    """
    kf_id = models.CharField(max_length=11, primary_key=True,
                             default=task_id)
    uuid = models.UUIDField(default=uuid.uuid4,
                            help_text='UUID used internally')
    state = models.CharField(max_length=100, choices=STATES, default='waiting',
                             help_text='The current state of the task')
    progress = models.IntegerField(default=0, help_text='Optional field'
                                   ' representing what percentage of the task'
                                   ' has been completed')
    release = models.ForeignKey(Release,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='tasks')
    task_service = models.ForeignKey(TaskService,
                                     on_delete=models.CASCADE,
                                     null=False,
                                     blank=False,
                                     related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Time the task was created')
