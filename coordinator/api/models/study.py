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
    name = models.CharField(max_length=256)
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

    @property
    def last_published_release(self):
        """
        Gets the last published release this study was in and stores it
        on the object for retrieval by other last_published_ functions.
        """
        from coordinator.api.models.release import Release
        if getattr(self, '_last_published_release', None):
            if self._last_published_release == 'no_releases':
                return None
            return self._last_published_release

        try:
            self._last_published_release = (self.release_set
                                                .filter(state='published')
                                                .latest('created_at'))
            return self._last_published_release
        except Release.DoesNotExist:
            # If there were no release, we will mark it as a special value
            # so as to prevent returning to the db for the same results
            self._last_published_release = 'no_releases'
            return None

    def last_published_version(self):
        """
        Gets the version number of the last published release that this
        study was in.
        """
        return getattr(self.last_published_release, 'version', None)

    def last_published_date(self):
        """
        Gets the date of the last published release that this study was in.
        """
        return getattr(self.last_published_release, 'created_at', None)
