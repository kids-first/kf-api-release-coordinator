from django.core.cache import cache
from graphene import relay, ObjectType, Field, Schema, String
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .releases import Query as ReleaseQuery, Mutation as ReleaseMutation
from .tasks import Query as TaskQuery
from .task_services import (
    Query as TaskServiceQuery,
    Mutation as TaskServiceMutation,
)
from .events import Query as EventQuery
from .release_notes import Query as ReleaseNoteQuery
from .studies import Query as StudyQuery, Mutation as StudyMutation
from .users import Query as UserQuery


def get_version_info():
    from coordinator.version_info import COMMIT, VERSION
    return {"commit": COMMIT, "version": VERSION}


class Status(ObjectType):
    name = String()
    version = String()
    commit = String()


class Query(
    ObjectType,
    ReleaseQuery,
    TaskQuery,
    TaskServiceQuery,
    EventQuery,
    ReleaseNoteQuery,
    StudyQuery,
    UserQuery,
):
    status = Field(Status)

    def resolve_status(parent, info):
        """
        Return status information about the coordinator.
        """
        # Retrieve from cache in the case that we have to parse git commands
        # to get version details.
        info = cache.get_or_set("VERSION_INFO", get_version_info)

        return Status(name="Kids First Release Coordinator", **info)


class Mutation(
    ObjectType, ReleaseMutation, TaskServiceMutation, StudyMutation
):
    pass


schema = Schema(query=Query, mutation=Mutation)
