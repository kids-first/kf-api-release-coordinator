import factory

from coordinator.api.models.taskservice import TaskService


class TaskServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TaskService

    name = factory.Faker("bs")
    author = factory.Faker("name")
    description = factory.Faker("bs")
