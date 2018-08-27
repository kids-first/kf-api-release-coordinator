from rest_framework import viewsets

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
