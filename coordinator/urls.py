from django.conf.urls import url, include
from rest_framework import routers
from coordinator.api import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'tasks', views.TaskViewSet)
router.register(r'task-services', views.TaskServiceViewSet)
router.register(r'releases', views.ReleaseViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^django-rq/', include('django_rq.urls')),
]
