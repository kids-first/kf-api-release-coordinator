import factory

from coordinator.api.models.task import Task


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    release = factory.SubFactory(
        "coordinator.api.factories.release.ReleaseFactory"
    )
    task_service = factory.SubFactory(
        "coordinator.api.factories.task_service.TaskServiceFactory"
    )
