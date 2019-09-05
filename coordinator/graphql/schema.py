from graphene import relay, ObjectType, Schema
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .releases import Query as ReleaseQuery
from .tasks import Query as TaskQuery
from .task_services import Query as TaskServiceQuery
from .events import Query as EventQuery


class Query(ObjectType, ReleaseQuery, TaskQuery, TaskServiceQuery, EventQuery):
    pass


schema = Schema(query=Query)
