import datetime
import uuid
import requests
from requests.exceptions import ConnectionError, HTTPError

import django_rq
from django.db import models
from django.conf import settings
from django_fsm import FSMField, transition
from django.core.cache import cache
from coordinator.authentication import get_service_token
from coordinator.utils import kf_id_generator
from coordinator.api.models.release import Release
from coordinator.api.models.taskservice import TaskService


def task_id():
    return kf_id_generator('TA')()


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
    state = FSMField(default='waiting',
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

    @transition(field=state, source='waiting', target='initialized')
    def initialize(self):
        return

    @transition(field=state, source='initialized', target='running')
    def start(self):
        return

    @transition(field=state, source='running', target='staged')
    def stage(self):
        return

    @transition(field=state, source='staged', target='publishing')
    def publish(self):
        return

    @transition(field=state, source='publishing', target='published')
    def complete(self):
        return

    @transition(field=state, source='waiting', target='rejected')
    def reject(self):
        return

    @transition(field=state, source='*', target='failed')
    def failed(self):
        return

    @transition(field=state, source='*', target='canceled')
    def cancel(self):
        return

    def status_check(self):
        """
        Update the task's status by pinging the Task Service for its status
        """
        from coordinator.tasks import cancel_release
        body = {
            'task_id': self.kf_id,
            'release_id': self.release_id,
            'action': 'get_status'
        }
        try:
            resp = requests.post(self.task_service.url+'/tasks',
                                 headers=cache.get_or_set(
                                    settings.CACHE_EGO_TOKEN,
                                    get_service_token
                                 ),
                                 json=body,
                                 timeout=settings.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except (ConnectionError, HTTPError):
            # Cancel release if there is a problem
            if self.release.state not in ['canceling', 'canceled']:
                self.release.cancel()
                self.release.save()
                django_rq.enqueue(cancel_release, self.release.kf_id,
                                  fail=True)
            self.failed()
            self.save()
            return

        resp = resp.json()

        if 'state' in resp and resp['state'] != self.state:
            if resp['state'] == 'canceled':
                self.cancel()
                self.release.cancel()
                self.release.save()
                django_rq.enqueue(cancel_release, self.release.kf_id)
                return
            elif resp['state'] == 'failed':
                from coordinator.tasks import cancel_release
                self.failed()
                self.release.cancel()
                self.release.save()
                django_rq.enqueue(cancel_release,
                                  self.release.kf_id,
                                  fail=True)
                return
            elif resp['state'] == 'staged' and self.state != 'staged':
                self.stage()
                self.save()
                # Check all tasks in release
                release = self.release
                if all([t.state == 'staged' for t in release.tasks.all()]):
                    release.staged()
                    release.save()
                return
            elif resp['state'] == 'published' and self.state != 'published':
                self.complete()
                self.save()
                # Check all tasks in release
                release = self.release
                if all([t.state == 'published' for t in release.tasks.all()]):
                    release.complete()
                    release.save()
                return

        # Check if the task has timed out
        if self.state not in ['staged', 'published', 'canceled', 'failed']:
            last_update = self.events.order_by('-created_at')\
                                     .first().created_at.replace(tzinfo=None)
            diff = datetime.datetime.utcnow() - last_update

            if diff.total_seconds() > settings.TASK_TIMEOUT:
                self.release.cancel()
                self.release.save()
                django_rq.enqueue(cancel_release, self.kf_id)
                return

        if 'progress' in resp and resp['progress'] != self.progress:
            if isinstance(resp['progress'], str):
                resp['progress'] = int(resp['progress'].replace('%', ''))
            self.progress = resp['progress']
        if not self.progress:
            self.progress = 0

        self.save()
