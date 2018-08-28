import requests
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from coordinator.api.models import Study, Release
from coordinator.api.serializers import StudySerializer, ReleaseSerializer


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
        if not settings.DATASERVICE_URL:
            return

        resp = requests.get(settings.DATASERVICE_URL+'/studies?limit=100')
        if resp.status_code != 200:
            message = 'There was an error getting studies from the dataservice'
            if resp.json() and 'message' in resp.json():
                message = resp.json()['message']
            return Response({'status': 'error',
                             'message': f'{message}'}, resp.status_code)

        studies = Study.objects.all()
        new = 0
        deleted = 0

        for study in resp.json()['results']:
            try:
                s = Study.objects.get(kf_id=study['kf_id'])
            # We don't know about the study, create it
            except Study.DoesNotExist:
                s = Study(kf_id=study['kf_id'],
                          name=study['name'],
                          visible=study['visible'],
                          created_at=study['created_at'])
                s.save()
                new += 1
                continue

            # Check for updated fields
            for field in ['name', 'visible']:
                if getattr(s, field) != study[field]:
                    setattr(s, field, study[field])
            s.save()

        # Check if any studies were deleted from the dataservice
        coord_studies = set(s.kf_id for s in studies)
        ds_studies = set(s['kf_id'] for s in resp.json()['results'])
        missing_studies = coord_studies - ds_studies
        deleted = len(missing_studies)
        for study in missing_studies:
            s = Study.objects.get(kf_id=study)
            s.deleted = True
            s.save()

        return Response({'status': 'ok',
                         'new': new,
                         'deleted': deleted,
                         'message': f'Synchronized with dataservice'}, 200)


class StudyReleasesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Returns a page of releases related to a given study
    """
    lookup_field = 'kf_id'
    serializer_class = ReleaseSerializer

    def get_queryset(self):
        return Study.objects.get(kf_id=self.kwargs['study_kf_id']) \
                            .release_set.order_by('-created_at')
