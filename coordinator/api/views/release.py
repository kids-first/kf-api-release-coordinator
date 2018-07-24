import django_rq
import django_fsm
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from rest_framework.mixins import UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from coordinator.authentication import EgoAuthentication
from coordinator.tasks import init_release, publish_release
from coordinator.permissions import GroupPermission
from coordinator.api.models import Release
from coordinator.api.serializers import ReleaseSerializer


class ReleaseViewSet(viewsets.ModelViewSet, UpdateModelMixin):
    """
    retrieve:
    Get a release by `kf_id`

    list:
    Return a page of releases

    update:
    Updates a release given a `kf_id` completely replacing any fields

    partial_update:
    Updates a release given a `kf_id` replacing only specified fields
    """
    authentication_classes = (EgoAuthentication,)
    permission_classes = (GroupPermission,)
    lookup_field = 'kf_id'
    queryset = Release.objects.order_by('-created_at').all()
    serializer_class = ReleaseSerializer

    def create(self, *args, **kwargs):
        """
        Create a new release given an array of study ids. This will trigger
        the begining of the release process.
        """
        res = super(ReleaseViewSet, self).create(*args, **kwargs)
        if res.status_code == 201:
            kf_id = res.data['kf_id']
            django_rq.enqueue(init_release, kf_id)
        return res

    def destroy(self, request, kf_id=None):
        """
        Cancel a release

        When a release is cancelled:
        - All running tasks should sent a cancel action
        - The release should not be deleted
        """
        try:
            release = Release.objects.get(kf_id=kf_id)
        except ObjectDoesNotExist:
            return Response({}, status=404)

        try:
            release.cancel()
            release.save()
        except django_fsm.TransitionNotAllowed:
            # Release must already be canceled or is canceling
            pass

        # Do other cancel logic here
        return self.retrieve(request, kf_id)

    @action(methods=['post'], detail=True)
    def publish(self, request, kf_id=None):
        """
        Begin the publish process for the release given a `kf_id`.
        Release must be in the `staged` state to begin publishing.
        """
        release = Release.objects.get(kf_id=kf_id)
        release.publish()
        release.save()
        django_rq.enqueue(publish_release, release.kf_id)
        return Response({'message': 'publishing'})
