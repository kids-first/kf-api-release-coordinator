import uuid
import datetime
from django.db import models
from django.contrib.postgres.fields import ArrayField


STATES= [
    ('pending', 'pending'),
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


class Task(models.Model):
    """
    A Task is a process that is run on a Task Service as part of a Release
    """
    kf_id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4,
                             help_text='Kids First ID assigned to the task')
    uuid = models.UUIDField(default=uuid.uuid4,
                            help_text='UUID used internally')
    state = models.CharField(max_length=100, choices=STATES, default='pending',
                             help_text='The current state of the task')
    progress = models.IntegerField(help_text='Optional field representing what'
                                   ' percentage of the task has been completed')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Time the task was created')


class TaskService(models.Model):
    """
    A Task Service runs a particular Task that is required for a release
    """
    kf_id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4,
                             help_text='Kids First ID assigned to the service')
    uuid = models.UUIDField(default=uuid.uuid4,
                            help_text='UUID used internally')
    name = models.CharField(max_length=100,
                            help_text='The name of the service')
    url = models.URLField(help_text='endpoint for the task\'s API')
    health_status = models.CharField(max_length=10, choices=STATUSES,
                                     default='green',
                                     help_text='The current status of the'
                                     ' task service')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Time the task was created')


class Release(models.Model):
    """
    A Release is composed of several tasks that run process that prepare and
    publish data for a release
    """
    kf_id = models.CharField(max_length=36, default=uuid.uuid4,
                             help_text='Kids First ID assigned to the'
                             ' release')
    uuid = models.UUIDField(default=uuid.uuid4,
                            help_text='UUID used internally')
    tasks = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    state = models.CharField(max_length=200, choices=STATES, default='pending',
                             help_text='The current state of the release')
    studies = ArrayField(models.CharField(max_length=11, blank=False),
                         help_text='kf_ids of the studies in this release')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Date created')
