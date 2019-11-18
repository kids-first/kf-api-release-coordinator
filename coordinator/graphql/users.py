import graphene
from graphene import relay, ObjectType, Field, List, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import FilterSet, OrderingFilter, NumberFilter

from graphql import GraphQLError
from django.contrib.auth import get_user_model

from coordinator.api.models.study import Study

User = get_user_model()


class UserNode(DjangoObjectType):
    roles = List(String, description="Roles that the user has")
    groups = List(String, description="Groups that the user belongs to")

    def resolve_roles(self, info):
        return self.auth_roles

    def resolve_groups(self, info):
        return self.auth_groups

    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "last_login",
            "date_joined",
            "picture",
            "study_subscriptions",
            "slack_notify",
            "slack_member_id",
        ]

    @classmethod
    def get_node(cls, info, sub):
        """
        Only return node if user is an admin or is self
        """
        try:
            obj = cls._meta.model.objects.get(sub=sub)
        except cls._meta.model.DoesNotExist:
            return None

        user = info.context.user

        if not user.is_authenticated:
            return None

        if user.is_admin:
            return obj

        if obj.sub == user.sub:
            return obj

        return None


class UserFilter(FilterSet):
    joined_before = NumberFilter(field_name="date_joined", lookup_expr="lt")
    joined_after = NumberFilter(field_name="date_joined", lookup_expr="gt")

    class Meta:
        model = User
        fields = {
            "email": ["exact", "contains"],
            "username": ["exact"],
            "first_name": ["exact"],
            "last_name": ["exact"],
            "last_login": ["gt", "lt"],
            "date_joined": ["gt", "lt"],
        }

    order_by = OrderingFilter(fields=("date_joined",))


class Query(object):
    all_users = DjangoFilterConnectionField(
        UserNode,
        filterset_class=UserFilter,
        description="Get all users known to th e Release Coordinator",
    )
    my_profile = Field(
        UserNode, description="Get the profile of the currently logged in user"
    )

    def resolve_all_users(self, info, **kwargs):
        """
        If user is USER, only return that user
        If user is ADMIN, return all users
        If user is unauthed, return no users
        """
        user = info.context.user

        if not user.is_authenticated or user is None:
            return User.objects.none()

        if user.is_admin or (
            "ADMIN" in user.auth_roles or "DEV" in user.auth_roles
        ):
            return User.objects.all()

        return [user]

    def resolve_my_profile(self, info, **kwargs):
        """
        Return the user that is making the request if they are valid,
        otherwise, return nothing
        """
        user = info.context.user

        # Unauthed and service users do not have profiles
        if not user.is_authenticated or user is None:
            raise GraphQLError("not authenticated as a user with a profile")

        return user
