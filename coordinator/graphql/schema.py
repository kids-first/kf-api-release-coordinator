from graphene import relay, ObjectType, Schema
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .releases import Query as ReleaseQuery
from .tasks import Query as TaskQuery
from .task_services import Query as TaskServiceQuery
from .events import Query as EventQuery
from .release_notes import Query as ReleaseNoteQuery
from .studies import Query as StudyQuery


class Query(
    ObjectType,
    ReleaseQuery,
    TaskQuery,
    TaskServiceQuery,
    EventQuery,
    ReleaseNoteQuery,
    StudyQuery,
):
    pass


schema = Schema(query=Query)
