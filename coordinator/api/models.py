import boto3
import datetime
import json
import uuid
import requests

from requests.exceptions import ConnectionError, HTTPError
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver


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

EVENTS = [
    ('info', 'info'),
    ('warning', 'warning'),
    ('error', 'error')
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


def event_id():
    return kf_id_generator('EV')()


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
            resp = requests.get(self.url+'/status')
            resp.raise_for_status()
        except (ConnectionError, HTTPError):
            self.last_ok_status += 1
            self.save()
            return

        if self.last_ok_status > 0:
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


class Event(models.Model):
    """
    An event holds a simple message and type that references an action that
    occurred on a release, task, or service

    :param kf_id: The kf_id of the event
    :param uuid: The uuid of the event
    :param event_type: The type of event, warning, info, or error.
    :param created_at: The time the event occurred
    """
    kf_id = models.CharField(max_length=11, primary_key=True,
                             default=task_id)
    uuid = models.UUIDField(default=uuid.uuid4,
                            help_text='UUID used internally')
    event_type = models.CharField(max_length=20,
                                  choices=EVENTS,
                                  default='info',
                                  help_text='The type of event')
    message = models.CharField(max_length=200,
                               help_text='The message describing the event')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Time the event was created')
    release = models.ForeignKey(Release,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='events')
    task_service = models.ForeignKey(TaskService,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True,
                                     related_name='events')
    task = models.ForeignKey(Task,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True,
                             related_name='events')


@receiver(post_save, sender=Event)
def send_sns(sender, instance, **kwargs):
    if settings.SNS_ARN is not None:
        client = boto3.client('sns')
        message = {
            'default': {
                'event_type': instance.event_type,
                'message': instance.message,
                'task_service': None,
                'task': None,
                'release': None
            }
        }
        if instance.task_service:
            message['default']['task_service'] = instance.task_service.kf_id
        if instance.task:
            message['default']['task'] = instance.task.kf_id
        if instance.release:
            message['default']['release'] = instance.release.kf_id

        message['default'] = json.dumps(message['default'])

        client.publish(TopicArn=settings.SNS_ARN,
                       MessageStructure='json',
                       Message=json.dumps(message))
