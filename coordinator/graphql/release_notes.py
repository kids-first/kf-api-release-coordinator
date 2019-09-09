from django_filters import CharFilter, FilterSet, NumberFilter, OrderingFilter
from graphene import relay, ObjectType
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from coordinator.api.models.release_note import ReleaseNote


class ReleaseNoteNode(DjangoObjectType):
    """ A release note for a release or a study within a release """

    class Meta:
        model = ReleaseNote
        filter_fields = {}
        interfaces = (relay.Node,)


class ReleaseNoteFilter(FilterSet):
    created_before = NumberFilter(field_name="created_at", lookup_expr="lt")
    created_after = NumberFilter(field_name="created_at", lookup_expr="gt")
    order_by = OrderingFilter(fields=("created_at",))

    class Meta:
        model = ReleaseNote
        fields = ["kf_id", "author", "release", "study"]


class Query:
    event = relay.Node.Field(
        ReleaseNoteNode, description="Retrieve a single release note"
    )
    all_release_notes = DjangoFilterConnectionField(
        ReleaseNoteNode,
        filterset_class=ReleaseNoteFilter,
        description="Get all release notes from the Coordinator",
    )

    def resolve_all_release_notes(self, info, **kwargs):
        """
        ADMIN - Return all release notes
        DEV - Return all release notes
        USER - Return release notes for all published releases and releases
            which have studies that the user is a member of.
        ANON - Return release notes for all published releases
        """
        user = info.context.user
        if hasattr(user, "roles") and (
            "ADMIN" in user.roles or "DEV" in user.roles
        ):
            return ReleaseNote.objects.all()

        if hasattr(user, "groups") and len(user.groups) > 0:
            return ReleaseNote.objects.filter(
                release__studies__kf_id__in=user.groups
            ) | ReleaseNote.objects.filter(release__state="published")

        return ReleaseNote.objects.filter(release__state="published").all()
