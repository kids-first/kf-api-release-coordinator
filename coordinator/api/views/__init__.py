from drf_yasg.generators import OpenAPISchemaGenerator
from coordinator.api.views.task import TaskViewSet
from coordinator.api.views.release import ReleaseViewSet
from coordinator.api.views.task_service import TaskServiceViewSet
from coordinator.api.views.event import EventViewSet


class SwaggerSchema(OpenAPISchemaGenerator):
    """ Custom schema generator to inject x-logo and remove security """
    def get_schema(self, request=None, public=False):
        schema = super(SwaggerSchema, self).get_schema(request, public)
        schema['info']['x-logo'] = {'url': '/static/kf_releasecoordinator.png'}
        del schema['security']
        del schema['securityDefinitions']
        return schema
