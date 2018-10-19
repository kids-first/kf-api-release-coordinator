import datetime
import uuid
import django_rq
import logging
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django_fsm import FSMField, transition
from semantic_version import Version
from semantic_version.django_fields import VersionField

from coordinator.utils import kf_id_generator
from coordinator.api.models.study import Study

# Allowed source statse for release cancels and fails
CANCEL_SOURCES = ['waiting', 'initializing', 'running', 'staged', 'publishing']
FAIL_SOURCES = CANCEL_SOURCES+['canceling']


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def release_id():
    return kf_id_generator('RE')()


def next_version(major=False, minor=False, patch=True):
    """
    Assign the next version by taking the version of the last release and
    bumping the patch number by one
    """
    try:
        r = Release.objects.latest()
    except Release.DoesNotExist:
        return Version('0.0.0')

    v = r.version
    if major:
        v = v.next_major()
    elif minor:
        v = v.next_minor()
    else:
        v = v.next_patch()
    return v


class Release(models.Model):
    """
    A Release is composed of several tasks that run process that prepare and
    publish data for a release
    """
    class Meta:
        get_latest_by = 'created_at'

    kf_id = models.CharField(max_length=11, primary_key=True,
                             default=release_id,
                             help_text='Kids First ID assigned to the'
                             ' release')
    uuid = models.UUIDField(default=uuid.uuid4,
                            help_text='UUID used internally')
    author = models.CharField(max_length=100, blank=False, default='admin',
                              help_text='The user who created the release')
    name = models.CharField(max_length=256,
                            help_text='Name of the release')
    description = models.CharField(max_length=5000, blank=True,
                                   help_text='Release notes')
    state = FSMField(default='waiting',
                     help_text='The current state of the release')
    tags = ArrayField(models.CharField(max_length=50, blank=True),
                      blank=True, default=list,
                      help_text='Tags to group the release by')
    studies = models.ManyToManyField(Study,
                                     help_text='kf_ids of the studies '
                                     'in this release')
    version = VersionField(partial=False, coerce=False,
                           default=next_version,
                           help_text='Semantic version of the release')
    is_major = models.BooleanField(default=False,
                                   help_text='Whether the release is a major '
                                   ' version change or not')
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
        if self.is_major:
            self.version = self.version.next_major()
        else:
            self.version = self.version.next_minor()
        self.save()
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
            logger.error(f'canceling release {self.kf_id} for time out.')
            self.cancel()
            self.save()
            django_rq.enqueue(cancel_release, self.kf_id)
            return

        # Check if any contained tasks have failed/canceled
        for task in self.tasks:
            if task.state in ['failed', 'canceled', 'rejected']:
                if self.state == 'canceling':
                    return
                logger.error(f'canceling release: {self.kf_id} task is ' +
                             f'{task.state}')
                self.cancel()
                self.save()
                django_rq.enqueue(cancel_release, self.kf_id)
                return
