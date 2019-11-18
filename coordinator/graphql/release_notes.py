from django_filters import CharFilter, FilterSet, NumberFilter, OrderingFilter
import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import from_global_id

from coordinator.api.models.release_note import ReleaseNote
from coordinator.api.models.release import Release
from coordinator.api.models.study import Study
from .releases import ReleaseNode
from .studies import StudyNode


class ReleaseNoteNode(DjangoObjectType):
    """ A release note for a release or a study within a release """

    class Meta:
        model = ReleaseNote
        filter_fields = {}
        interfaces = (graphene.relay.Node,)


class ReleaseNoteFilter(FilterSet):
    created_before = NumberFilter(field_name="created_at", lookup_expr="lt")
    created_after = NumberFilter(field_name="created_at", lookup_expr="gt")
    order_by = OrderingFilter(fields=("created_at",))

    class Meta:
        model = ReleaseNote
        fields = ["kf_id", "author", "release", "study"]


class ReleaseNoteInput(graphene.InputObjectType):
    description = graphene.String(
        required=True,
        description="Description of changes made to a study within a release",
    )
    study = graphene.ID(
        required=True, description="Study that the note describes"
    )
    release = graphene.ID(
        required=True,
        description="Release that the study the note describes is in",
    )


class CreateReleaseNote(graphene.Mutation):
    class Arguments:
        input = ReleaseNoteInput(required=True)

    release_note = graphene.Field(ReleaseNoteNode)

    @staticmethod
    def mutate(root, info, input=None):
        """
        Create a new release note for a study in a release.
        """
        user = info.context.user
        if not hasattr(user, "auth_roles") or (
            "ADMIN" not in user.auth_roles and "DEV" not in user.auth_roles
        ):
            raise GraphQLError("Not authenticated to create a release note.")

        try:
            _, study_id = from_global_id(input.get("study"))
            study = Study.objects.get(kf_id=study_id)
            del input["study"]
        except Study.DoesNotExist as err:
            raise GraphQLError(f"Study {study_id} does not exist")

        try:
            _, release_id = from_global_id(input.get("release"))
            release = Release.objects.get(kf_id=release_id)
            del input["release"]
        except Release.DoesNotExist as err:
            raise GraphQLError(f"Release {release_id} does not exist")

        if not release.studies.filter(pk=study_id).exists():
            raise GraphQLError(
                f"Study {study_id} is not in release {release_id}"
            )

        release_note = ReleaseNote(**input)
        release_note.author = user.username
        release_note.release = release
        release_note.study = study
        release_note.save()

        return CreateReleaseNote(release_note=release_note)


class UpdateReleaseNoteInput(graphene.InputObjectType):
    description = graphene.String(
        required=True,
        description="Description of changes made to a study within a release",
    )


class UpdateReleaseNote(graphene.Mutation):
    class Arguments:
        release_note = graphene.ID(
            required=True, description="The release note to update"
        )
        input = UpdateReleaseNoteInput(required=True)

    release_note = graphene.Field(ReleaseNoteNode)

    @staticmethod
    def mutate(root, info, release_note, input):
        """
        Update an existing release note
        """
        user = info.context.user
        if not hasattr(user, "auth_roles") or (
            "ADMIN" not in user.auth_roles and "DEV" not in user.auth_roles
        ):
            raise GraphQLError("Not authenticated to update a release note.")

        try:
            _, release_note_id = from_global_id(release_note)
            release_note = ReleaseNote.objects.get(kf_id=release_note_id)
        except ReleaseNote.DoesNotExist as err:
            raise GraphQLError(
                f"Release note {release_note_id} does not exist"
            )

        if "description" in input:
            release_note.description = input["description"]

        release_note.save()

        return UpdateReleaseNote(release_note=release_note)


class RemoveReleaseNote(graphene.Mutation):
    class Arguments:
        release_note = graphene.ID(
            required=True, description="The release note to remove"
        )

    success = graphene.Boolean()

    @staticmethod
    def mutate(root, info, release_note):
        """
        Delete an existing release note
        """
        user = info.context.user
        if not hasattr(user, "auth_roles") or (
            "ADMIN" not in user.auth_roles and "DEV" not in user.auth_roles
        ):
            raise GraphQLError("Not authenticated to delete a release note.")

        try:
            _, release_note_id = from_global_id(release_note)
            release_note = ReleaseNote.objects.get(kf_id=release_note_id)
        except ReleaseNote.DoesNotExist as err:
            raise GraphQLError(
                f"Release note {release_note_id} does not exist"
            )

        release_note.delete()

        return RemoveReleaseNote(success=True)


class Query:
    event = graphene.relay.Node.Field(
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
        if hasattr(user, "auth_roles") and (
            "ADMIN" in user.auth_roles or "DEV" in user.auth_roles
        ):
            return ReleaseNote.objects.all()

        if hasattr(user, "auth_groups") and len(user.auth_groups) > 0:
            return ReleaseNote.objects.filter(
                release__studies__kf_id__in=user.auth_groups
            ) | ReleaseNote.objects.filter(release__state="published")

        return ReleaseNote.objects.filter(release__state="published").all()


class Mutation:
    create_release_note = CreateReleaseNote.Field(
        description="Create a new release note for a given study in release"
    )
    update_release_note = UpdateReleaseNote.Field(
        description="Update an existing release note"
    )
    remove_release_note = RemoveReleaseNote.Field(
        description="Remove an existing release note"
    )
