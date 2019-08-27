from django_filters import CharFilter, FilterSet, NumberFilter, OrderingFilter
from graphene import relay, ObjectType, String
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from coordinator.api.models.taskservice import TaskService


class TaskServiceNode(DjangoObjectType):
    """ A task service in the TaskService Coordinator """

    health_status = String(
        resolver=lambda obj, _: obj.health_status,
        description="Current status of the task service",
    )

    class Meta:
        model = TaskService
        interfaces = (relay.Node,)


class TaskServiceFilter(FilterSet):
    name_contains = CharFilter(field_name="name", lookup_expr="icontains")
    created_before = NumberFilter(field_name="created_at", lookup_expr="lt")
    created_after = NumberFilter(field_name="created_at", lookup_expr="gt")
    order_by = OrderingFilter(fields=("created_at",))

    class Meta:
        model = TaskService
        fields = ["author", "name", "url", "description", "enabled"]


class Query:
    task_service = relay.Node.Field(
        TaskServiceNode, description="Retrieve a single task service"
    )
    all_task_services = DjangoFilterConnectionField(
        TaskServiceNode,
        filterset_class=TaskServiceFilter,
        description="Get all task services from the Coordinator",
    )

    def resolve_all_task_services(self, info, **kwargs):
        user = info.context.user
        if hasattr(user, "roles") and (
            "ADMIN" in user.roles or "DEV" in user.roles
        ):
            return TaskService.objects.all()

        return TaskService.objects.none()
