from rest_framework import viewsets
from drf_yasg.generators import OpenAPISchemaGenerator
from coordinator.api.models import Event
from coordinator.api.serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Get an event by `kf_id`

    create:
    Register a new event

    list:
    Return a page of events

    update:
    Updates an event  given a `kf_id` completely replacing any fields

    partial_update:
    Updates an event given a `kf_id` replacing only specified fields

    destroy:
    Completely remove the event from the coordinator.
    """
    lookup_field = 'kf_id'
    serializer_class = EventSerializer

    def get_queryset(self):
        """
        Filter by relase, task_sevice, and/or task
        """
        queryset = Event.objects.order_by('-created_at')

        for field_name in ['release', 'task_service', 'task']:
            field = self.request.query_params.get(field_name, None)
            if field is not None:
                kwargs = {field_name: field}
                queryset = queryset.filter(**kwargs)

        return queryset


class SwaggerSchema(OpenAPISchemaGenerator):
    """ Custom schema generator to inject x-logo and remove security """
    def get_schema(self, request=None, public=False):
        schema = super(SwaggerSchema, self).get_schema(request, public)
        schema['info']['x-logo'] = {'url': '/static/kf_releasecoordinator.png'}
        del schema['security']
        del schema['securityDefinitions']
        return schema
