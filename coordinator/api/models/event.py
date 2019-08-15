import uuid

from django.db import models

from coordinator.utils import kf_id_generator
from coordinator.api.models.task import Task
from coordinator.api.models.release import Release
from coordinator.api.models.taskservice import TaskService


EVENTS = [
    ('info', 'info'),
    ('warning', 'warning'),
    ('error', 'error')
]


def event_id():
    return kf_id_generator('EV')()


class Event(models.Model):
    """
    An event holds a simple message and type that references an action that
    occurred on a release, task, or service

    :param kf_id: The kf_id of the event
    :param uuid: The uuid of the event
    :param event_type: The type of event, warning, info, or error.
    :param created_at: The time the event occurred
    """
    kf_id = models.CharField(max_length=11, primary_key=True, default=event_id)
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
