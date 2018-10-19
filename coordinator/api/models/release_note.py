import uuid

from django.db import models

from coordinator.utils import kf_id_generator
from coordinator.api.models.release import Release
from coordinator.api.models.study import Study


def release_note_id():
    return kf_id_generator('RN')()


class ReleaseNote(models.Model):
    """
    Release notes describe changes to a study made in a release.

    :param kf_id: The kf_id of the note
    :param uuid: The uuid of the note
    :param author: The author of the note
    :param description: The content of the note
    :param created_at: The time the note was created
    :param study: The study that the note describes
    :param release: The release that the study being described is in
    """
    kf_id = models.CharField(max_length=11, primary_key=True,
                             default=release_note_id)
    uuid = models.UUIDField(default=uuid.uuid4,
                            help_text='UUID used internally')
    author = models.CharField(max_length=100, blank=False, default='admin',
                              help_text='The user who created the note')
    description = models.CharField(max_length=5000,
                                   help_text='The content of the note')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Time the note was created')
    release = models.ForeignKey(Release,
                                on_delete=models.CASCADE,
                                null=False,
                                related_name='notes')
    study = models.ForeignKey(Study,
                              on_delete=models.SET_NULL,
                              null=True,
                              related_name='notes')
