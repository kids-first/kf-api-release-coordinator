from django_filters import CharFilter, FilterSet, NumberFilter, OrderingFilter
import graphene
import django_rq
import django_fsm
from graphql import GraphQLError
from graphql_relay import from_global_id
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from coordinator.tasks import init_release, cancel_release, publish_release

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


class CancelRelease(graphene.Mutation):
    class Arguments:
        release = graphene.ID(required=True)

    release = graphene.Field(ReleaseNode)

    @staticmethod
    def mutate(root, info, release):
        """
        Cancel a release
        """
        user = info.context.user
        if not hasattr(user, "roles") or (
            "ADMIN" not in user.roles and "DEV" not in user.roles
        ):
            raise GraphQLError("Not authenticated to cancel a release.")

        _, kf_id = from_global_id(release)

        try:
            release = Release.objects.get(kf_id=kf_id)
        except Release.DoesNotExist:
            raise GraphQLError("The release was not found.")

        try:
            release.cancel()
            release.save()
        except django_fsm.TransitionNotAllowed:
            # Release must already be canceled or is canceling
            raise GraphQLError(
                f"The release in state {release.state} may not be canceled."
            )

        django_rq.enqueue(cancel_release, release.kf_id)

        return CancelRelease(release=release)


class PublishRelease(graphene.Mutation):
    class Arguments:
        release = graphene.ID(required=True)

    release = graphene.Field(ReleaseNode)

    @staticmethod
    def mutate(root, info, release):
        """
        Publish a staged release.

        Only releases that have made it to the staged state may be published
        by an administrator.
        """
        user = info.context.user
        if not hasattr(user, "roles") or "ADMIN" not in user.roles:
            raise GraphQLError("Not authenticated to publish a release.")

        _, kf_id = from_global_id(release)

        try:
            release = Release.objects.get(kf_id=kf_id)
        except Release.DoesNotExist:
            raise GraphQLError("The release was not found.")

        try:
            release.publish()
            release.save()
        except django_fsm.TransitionNotAllowed:
            raise GraphQLError(
                f"The release in state {release.state} may not be published."
            )

        django_rq.enqueue(publish_release, release.kf_id)

        return CancelRelease(release=release)


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
    cancel_release = CancelRelease.Field(description="Cancel a release")
    publish_release = PublishRelease.Field(description="Publish a release")
