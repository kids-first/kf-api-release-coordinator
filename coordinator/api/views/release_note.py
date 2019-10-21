from rest_framework import viewsets
import django_filters.rest_framework

from coordinator.permissions import AdminOrReadOnlyPermission
from coordinator.api.serializers import ReleaseNoteSerializer
from coordinator.api.models import ReleaseNote


class ReleaseNoteFilter(django_filters.FilterSet):

    class Meta:
        model = ReleaseNote
        fields = ('author', 'study', 'release')


class ReleaseNoteViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Get a note by `kf_id`

    create:
    Register a new note

    list:
    Return a page of notes

    update:
    Updates an note given a `kf_id` completely replacing any fields

    partial_update:
    Updates an note given a `kf_id` replacing only specified fields

    destroy:
    Completely remove the note from the coordinator.
    """

    permission_classes = (AdminOrReadOnlyPermission,)
    lookup_field = "kf_id"
    queryset = ReleaseNote.objects.order_by("-created_at").all()
    serializer_class = ReleaseNoteSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = ReleaseNoteFilter
