from django_filters import CharFilter, FilterSet, NumberFilter, OrderingFilter
from graphene import relay, ObjectType
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from coordinator.api.models.event import Event


class EventNode(DjangoObjectType):
    """ An event in the Release Coordinator """

    class Meta:
        model = Event
        filter_fields = {}
        interfaces = (relay.Node,)


class EventFilter(FilterSet):
    message_contains = CharFilter(
        field_name="message", lookup_expr="icontains"
    )
    created_before = NumberFilter(field_name="created_at", lookup_expr="lt")
    created_after = NumberFilter(field_name="created_at", lookup_expr="gt")
    order_by = OrderingFilter(fields=("created_at",))

    class Meta:
        model = Event
        fields = ["event_type", "release", "task_service", "task"]


class Query:
    event = relay.Node.Field(EventNode, description="Retrieve a single event")
    all_events = DjangoFilterConnectionField(
        EventNode,
        filterset_class=EventFilter,
        description="Get all events from the Coordinator",
    )

    def resolve_all_events(self, info, **kwargs):
        """
        Return all events for admins and developers.
        Return events for all published releases and releases which have
            studies that the user is a member of.
        Only return events for published releases for everyone else.
        """
        user = info.context.user
        if hasattr(user, "roles") and (
            "ADMIN" in user.roles or "DEV" in user.roles
        ):
            return Event.objects.all()

        if hasattr(user, "groups") and len(user.groups) > 0:
            return (
                Event.objects.filter(release__studies__kf_id__in=user.groups)
                | Event.objects.filter(release__state="published")
            )

        return Event.objects.filter(release__state="published").all()
