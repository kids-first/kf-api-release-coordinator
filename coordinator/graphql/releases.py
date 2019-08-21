from django_filters import CharFilter, FilterSet, NumberFilter, OrderingFilter
from graphene import relay, ObjectType
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from coordinator.api.models.release import Release


class ReleaseNode(DjangoObjectType):
    """ A data release in Kids First """

    class Meta:
        model = Release
        filter_fields = {}
        interfaces = (relay.Node,)


class ReleaseFilter(FilterSet):
    name_contains = CharFilter(field_name="name", lookup_expr="icontains")
    created_before = NumberFilter(field_name="created_at", lookup_expr="lt")
    created_after = NumberFilter(field_name="created_at", lookup_expr="gt")
    order_by = OrderingFilter(fields=("created_at",))

    class Meta:
        model = Release
        fields = [
            "kf_id",
            "version",
            "state",
            "author",
            "name",
            "created_at",
            "is_major",
        ]


class Query:
    release = relay.Node.Field(
        ReleaseNode, description="Retrieve a single release"
    )
    all_releases = DjangoFilterConnectionField(
        ReleaseNode,
        filterset_class=ReleaseFilter,
        description="Get all releases from the Coordinator",
    )

    def resolve_all_releases(self, info, **kwargs):
        return Release.objects.all()
