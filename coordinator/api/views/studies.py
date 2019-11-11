import requests
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from coordinator.api.models import Study, Release
from coordinator.api.serializers import StudySerializer, ReleaseSerializer
from coordinator.dataservice import sync


class StudiesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Only read studies or sync studies with the dataservice.

    list:
    Returns a page of studies
    """
    lookup_field = 'kf_id'
    queryset = Study.objects.order_by('-created_at').all()
    serializer_class = StudySerializer

    @action(methods=['post'], detail=False)
    def sync(self, request):
        """
        Synchronize studies with the dataservice

        Currently done within a request with the intent that the user sync
        manually from the ui and recieve fresh studies on the response

        If the process for syncing studies becomes automated, then this
        may be moved to a task
        """

        try:
            new, deleted = sync()
        except requests.exceptions.RequestException as err:
            message = "There was an error getting studies from the dataservice"
            return Response(
                {"status": "error", "message": f"{message}"},
                err.response.status_code,
            )

        return Response(
            {
                "status": "ok",
                "new": len(new),
                "deleted": len(deleted),
                "message": f"Synchronized with dataservice",
            },
            200,
        )


class StudyReleasesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Returns a page of releases related to a given study
    """
    lookup_field = 'kf_id'
    serializer_class = ReleaseSerializer

    def get_queryset(self):
        return Study.objects.get(kf_id=self.kwargs['study_kf_id']) \
                            .releases.order_by('-created_at')
