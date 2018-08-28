import os
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_nested import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from coordinator.api import views


dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, 'README.md'), 'r') as f:
    description = f.read()


schema_view = get_schema_view(
   openapi.Info(
      title="Release Coordinator API",
      default_version='1.0.0',
      description=description,
      license=openapi.License(name="Apache 2.0"),
   ),
   generator_class=views.SwaggerSchema,
   public=True,
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'tasks', views.TaskViewSet)
router.register(r'task-services', views.TaskServiceViewSet)
router.register(r'releases', views.ReleaseViewSet)
router.register(r'events', views.EventViewSet, 'events-detail')
router.register(r'studies', views.StudiesViewSet, 'studies')

study_router = routers.NestedSimpleRouter(router, r'studies',
                                          trailing_slash=False,
                                          lookup='study')
study_router.register(r'releases', views.StudyReleasesViewSet,
                      base_name='study-releases')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(study_router.urls)),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None),
        name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None),
        name='schema-redoc'),
]
