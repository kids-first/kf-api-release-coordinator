import graphene
from django_filters import CharFilter, FilterSet, NumberFilter, OrderingFilter
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from coordinator.api.models.study import Study
from coordinator.dataservice import sync
from .releases import ReleaseNode, ReleaseFilter


class StudyNode(DjangoObjectType):
    """ A study in the release coordinator """

    releases = DjangoFilterConnectionField(
        ReleaseNode,
        filterset_class=ReleaseFilter,
        description="Get releases for a study",
    )

    class Meta:
        model = Study
        filter_fields = {}
        interfaces = (graphene.relay.Node,)


class StudyFilter(FilterSet):
    name_contains = CharFilter(field_name="name", lookup_expr="icontains")
    created_before = NumberFilter(field_name="created_at", lookup_expr="lt")
    created_after = NumberFilter(field_name="created_at", lookup_expr="gt")
    order_by = OrderingFilter(fields=("created_at",))
    name_contains = CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Study
        fields = ["kf_id", "visible", "deleted"]


class SyncStudies(graphene.Mutation):
    new = DjangoFilterConnectionField(StudyNode)
    deleted = DjangoFilterConnectionField(StudyNode)

    @staticmethod
    def mutate(root, info):
        """
        Synchronize studies with the dataservice
        """
        user = info.context.user
        if not hasattr(user, "roles") or (
            "ADMIN" not in user.roles and "DEV" not in user.roles
        ):
            raise GraphQLError("Not authenticated to sync studies.")

        try:
            new, deleted = sync()
        except requests.exceptions.RequestException as err:
            raise GraphQLError(
                "Problem getting studies from the Data Service: {err}"
            )

        return SyncStudies(new=new, deleted=deleted)


class Query:
    study = graphene.relay.Node.Field(
        StudyNode, description="Retrieve a single study"
    )
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


class Mutation:
    sync_studies = SyncStudies.Field(
        description="Synchronize studies with the dataservice"
    )
