import factory

from coordinator.api.factories.release import ReleaseFactory
from coordinator.api.factories.task_service import TaskServiceFactory
from coordinator.api.models.task import Task

class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task


    release = factory.SubFactory(ReleaseFactory)
    task_service = factory.SubFactory(TaskServiceFactory)
