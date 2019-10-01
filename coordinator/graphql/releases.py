from django_filters import CharFilter, FilterSet, NumberFilter, OrderingFilter
import graphene
import django_rq
from graphql import GraphQLError
from graphql_relay import from_global_id
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from coordinator.tasks import init_release

from coordinator.api.models.release import Release


class ReleaseNode(DjangoObjectType):
    """ A data release in Kids First """

    class Meta:
        model = Release
        filter_fields = {}
        interfaces = (graphene.relay.Node,)


class ReleaseFilter(FilterSet):
    name_contains = CharFilter(field_name="name", lookup_expr="icontains")
    created_before = NumberFilter(field_name="created_at", lookup_expr="lt")
    created_after = NumberFilter(field_name="created_at", lookup_expr="gt")
    order_by = OrderingFilter(fields=("created_at",))

    class Meta:
        model = Release
        fields = ["version", "state", "author", "name", "is_major"]


class ReleaseInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=False)
    is_major = graphene.Boolean(required=False)
    studies = graphene.List(graphene.ID, required=True)


class StartRelease(graphene.Mutation):
    class Arguments:
        input = ReleaseInput(required=True)

    release = graphene.Field(ReleaseNode)

    @staticmethod
    def mutate(root, info, input=None):
        """
        Create a new release and start the release process
        """
        user = info.context.user
        if not hasattr(user, "roles") or (
            "ADMIN" not in user.roles and "DEV" not in user.roles
        ):
            raise GraphQLError("Not authenticated to create a release.")

        studies = [from_global_id(study)[1] for study in input.get("studies")]
        del input["studies"]

        release = Release(**input)
        release.author = user.username
        release.save()
        release.studies.set(studies)
        release.save()

        django_rq.enqueue(init_release, release.kf_id)

        return StartRelease(release=release)


class Query:
    release = graphene.relay.Node.Field(
        ReleaseNode, description="Retrieve a single release"
    )
    all_releases = DjangoFilterConnectionField(
        ReleaseNode,
        filterset_class=ReleaseFilter,
        description="Get all releases from the Coordinator",
    )

    def resolve_all_releases(self, info, **kwargs):
        user = info.context.user
        if hasattr(user, "roles") and (
            "ADMIN" in user.roles or "DEV" in user.roles
        ):
            return Release.objects.all()

        return Release.objects.filter(state="published").all()


class Mutation:
    start_release = StartRelease.Field(description="Start a new release")
