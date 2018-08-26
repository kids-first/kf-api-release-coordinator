import datetime
import uuid
import django_rq
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django_fsm import FSMField, transition

from coordinator.utils import kf_id_generator
from coordinator.api.models.study import Study

# Allowed source statse for release cancels and fails
CANCEL_SOURCES = ['waiting', 'initializing', 'running', 'staged', 'publishing']
FAIL_SOURCES = CANCEL_SOURCES+['canceling']


def release_id():
    return kf_id_generator('RE')()


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
    state = FSMField(default='waiting',
                     help_text='The current state of the release')
    tags = ArrayField(models.CharField(max_length=50, blank=True),
                      blank=True, default=[],
                      help_text='Tags to group the release by')
    studies = models.ManyToManyField(Study,
                                     help_text='kf_ids of the studies '
                                     'in this release')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Date created')

    @transition(field=state, source='waiting', target='initializing')
    def initialize(self):
        """ Begin initializing tasks """
        return

    @transition(field=state, source='initializing', target='running')
    def start(self):
        """ Start the release """
        return

    @transition(field=state, source='running', target='staged')
    def staged(self):
        """ The release has been staged """
        return

    @transition(field=state, source='staged', target='publishing')
    def publish(self):
        """ Start publishing the release """
        return

    @transition(field=state, source='publishing', target='published')
    def complete(self):
        """ Complete publishing """
        return

    @transition(field=state, source=CANCEL_SOURCES, target='canceling')
    def cancel(self):
        """ Cancel the release """
        return

    @transition(field=state, source='canceling', target='canceled')
    def canceled(self):
        """ The release has finished canceling """
        return

    @transition(field=state, source=FAIL_SOURCES, target='failed')
    def failed(self):
        """ The release failed """
        return

    def status_check(self):
        """
        Check if the release has timed out and the state of all tasks in
        the release
        """
        from coordinator.tasks import cancel_release
        # Check if we hit the time limit
        last_update = self.events.order_by('-created_at')\
                                 .first().created_at
        diff = datetime.datetime.utcnow() - last_update.replace(tzinfo=None)

        if diff.total_seconds() > settings.RELEASE_TIMEOUT:
            if self.state == 'canceling':
                return
            self.cancel()
            self.save()
            django_rq.enqueue(cancel_release, self.kf_id)
            return

        # Check if any contained tasks have failed/canceled
        for task in self.tasks:
            if task.state in ['failed', 'canceled', 'rejected']:
                if self.state == 'canceling':
                    return
                self.cancel()
                self.save()
                django_rq.enqueue(cancel_release, self.kf_id)
                return
