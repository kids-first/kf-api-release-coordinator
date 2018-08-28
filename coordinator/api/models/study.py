from django.db import models


class Study(models.Model):
    """
    A study from the dataservice.
    Only store the kf_id and the name of the study.

    :param kf_id: The Kids First identifier, 'SD' prefix
    :param name: The name of the study
    :param visible: Whether or not the study is visible in the dataservice
    :param deleted: Whether the study was deleted from the dataservice
    :param created_at: The time that the task was registered with the
        coordinator.
    """
    kf_id = models.CharField(max_length=11, primary_key=True,
                             null=False)
    name = models.CharField(max_length=100)
    visible = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=False,
                                      null=True,
                                      help_text='Time the task was created')

    def latest_version(self):
        """
        Gets the latest version from the last release this study was in.
        """
        from coordinator.api.models.release import Release
        try:
            return self.release_set.latest('created_at').version
        except Release.DoesNotExist:
            return None
