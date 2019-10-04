import graphene
from graphql import GraphQLError
from graphql_relay import from_global_id
from django.core.exceptions import ValidationError
from django_filters import CharFilter, FilterSet, NumberFilter, OrderingFilter
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from coordinator.api.models.taskservice import TaskService
from coordinator.api.validators import validate_endpoint


class TaskServiceNode(DjangoObjectType):
    """ A task service in the TaskService Coordinator """

    health_status = graphene.String(
        resolver=lambda obj, _: obj.health_status,
        description="Current status of the task service",
    )

    class Meta:
        model = TaskService
        interfaces = (graphene.relay.Node,)


class TaskServiceFilter(FilterSet):
    name_contains = CharFilter(field_name="name", lookup_expr="icontains")
    created_before = NumberFilter(field_name="created_at", lookup_expr="lt")
    created_after = NumberFilter(field_name="created_at", lookup_expr="gt")
    order_by = OrderingFilter(fields=("created_at",))

    class Meta:
        model = TaskService
        fields = ["author", "name", "url", "description", "enabled"]


class TaskServiceInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=False)
    url = graphene.String(required=True)
    enabled = graphene.Boolean(required=False)


class CreateTaskService(graphene.Mutation):
    class Arguments:
        input = TaskServiceInput(required=True)

    task_service = graphene.Field(TaskServiceNode)

    @staticmethod
    def mutate(root, info, input=None):
        """
        Create a new task service
        """
        user = info.context.user
        if not hasattr(user, "roles") or (
            "ADMIN" not in user.roles and "DEV" not in user.roles
        ):
            raise GraphQLError("Not authenticated to create a task service.")

        try:
            validate_endpoint(input["url"])
        except (ValidationError, ValueError) as err:
            raise GraphQLError(
                f"There was a problem with the service url: {err}"
            )

        service = TaskService(**input)
        service.author = user.username
        service.save()

        return CreateTaskService(task_service=service)


class UpdateTaskService(graphene.Mutation):
    class Arguments:
        task_service = graphene.ID(required=True)
        input = TaskServiceInput(required=True)

    task_service = graphene.Field(TaskServiceNode)

    @staticmethod
    def mutate(root, info, task_service, input=None):
        """
        Updates a task service
        """
        user = info.context.user
        if not hasattr(user, "roles") or (
            "ADMIN" not in user.roles and "DEV" not in user.roles
        ):
            raise GraphQLError("Not authenticated to create a task service.")

        try:
            validate_endpoint(input["url"])
        except (ValidationError, ValueError) as err:
            raise GraphQLError(
                f"There was a problem with the service url: {err}"
            )

        _, kf_id = from_global_id(task_service)
        service = TaskService.objects.get(kf_id=kf_id)
        for k, v in input.items():
            setattr(service, k, v)
        service.save()

        return UpdateTaskService(task_service=service)


class Query:
    task_service = graphene.relay.Node.Field(
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


class Mutation:
    create_task_service = CreateTaskService.Field(
        description="Register a new task service"
    )
    update_task_service = UpdateTaskService.Field(
        description="Update a task service"
    )
