from graphene import relay, ObjectType, Schema
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .releases import Query as ReleaseQuery
from .tasks import Query as TaskQuery
from .task_services import Query as TaskServiceQuery


class Query(ObjectType, ReleaseQuery, TaskQuery, TaskServiceQuery):
    pass


schema = Schema(query=Query)
