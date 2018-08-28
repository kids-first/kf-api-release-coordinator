import requests
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from coordinator.api.models import Study
from coordinator.api.serializers import StudySerializer


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
        updated = 0
        deleted = 0

        for study in resp.json()['results']:
            try:
                s = Study.objects.get(kf_id=study['kf_id'])
            # We don't know about the study, create it
            except Study.DoesNotExist:
                s = Study(kf_id=study['kf_id'],
                          name=study['name'],
                          created_at=study['created_at'])
                s.save()
                new += 1
                continue

            # Check for updated fields
            for field in ['name']:
                if getattr(s, field) != study[field]:
                    setattr(s, field, study[field])
            s.save()

        return Response({'status': 'ok',
                         'message': f''}, 200)
