from graphene import relay, ObjectType, Schema
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .releases import Query as ReleaseQuery
from .tasks import Query as TaskQuery


class Query(ObjectType, ReleaseQuery, TaskQuery):
    pass


schema = Schema(query=Query)
