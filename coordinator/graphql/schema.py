from graphene import relay, ObjectType, Schema
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .releases import Query as ReleaseQuery


class Query(ObjectType, ReleaseQuery):
    pass


schema = Schema(query=Query)
