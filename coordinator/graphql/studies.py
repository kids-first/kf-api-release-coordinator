from django_filters import CharFilter, FilterSet, NumberFilter, OrderingFilter
from graphene import relay, ObjectType
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from coordinator.api.models.study import Study


class StudyNode(DjangoObjectType):
    """ A study in the release coordinator """

    class Meta:
        model = Study
        filter_fields = {}
        interfaces = (relay.Node,)


class StudyFilter(FilterSet):
    name_contains = CharFilter(field_name="name", lookup_expr="icontains")
    created_before = NumberFilter(field_name="created_at", lookup_expr="lt")
    created_after = NumberFilter(field_name="created_at", lookup_expr="gt")
    order_by = OrderingFilter(fields=("created_at",))

    class Meta:
        model = Study
        fields = ["kf_id", "visible", "deleted"]


class Query:
    study = relay.Node.Field(StudyNode, description="Retrieve a single study")
    all_studies = DjangoFilterConnectionField(
        StudyNode,
        filterset_class=StudyFilter,
        description="Get all studies from the Coordinator",
    )

    def resolve_all_studies(self, info, **kwargs):
        user = info.context.user
        if hasattr(user, "roles") and (
            "ADMIN" in user.roles or "DEV" in user.roles
        ):
            return Study.objects.all()

        return Study.objects.filter(visible=True).filter(deleted=False).all()
