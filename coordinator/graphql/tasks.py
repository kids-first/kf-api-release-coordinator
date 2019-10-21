from django_filters import (
    CharFilter,
    FilterSet,
    NumberFilter,
    CharFilter,
    OrderingFilter,
)
from graphene import relay, ObjectType
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from coordinator.api.models.task import Task


class TaskNode(DjangoObjectType):
    """ A task run on a task service during a release """

    class Meta:
        model = Task
        filter_fields = {}
        interfaces = (relay.Node,)


class TaskFilter(FilterSet):
    created_before = NumberFilter(field_name="created_at", lookup_expr="lt")
    created_after = NumberFilter(field_name="created_at", lookup_expr="gt")
    release = CharFilter(field_name="release__kf_id")
    task_service = CharFilter(field_name="task_service__kf_id")
    order_by = OrderingFilter(fields=("created_at",))

    class Meta:
        model = Task
        fields = ["kf_id", "state"]


class Query:
    task = relay.Node.Field(TaskNode, description="Retrieve a single task")
    all_tasks = DjangoFilterConnectionField(
        TaskNode,
        filterset_class=TaskFilter,
        description="Get all tasks from the Coordinator",
    )

    def resolve_all_tasks(self, info, **kwargs):
        user = info.context.user
        if hasattr(user, "auth_roles") and (
            "ADMIN" in user.auth_roles or "DEV" in user.auth_roles
        ):
            return Task.objects.all()

        queryset = Task.objects.filter(release__state="published")

        # Return tasks from any releases that the user has a study in
        if user and hasattr(user, "auth_groups") and len(user.auth_groups) > 0:
            queryset = queryset | Task.objects.filter(
                release__studies__kf_id__in=user.auth_groups
            )

        return queryset
