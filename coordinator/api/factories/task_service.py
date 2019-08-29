import factory

from coordinator.api.models.taskservice import TaskService


class TaskServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TaskService
        django_get_or_create = ("kf_id",)

    kf_id = factory.Sequence(lambda n: f"SD_{(n%3):08}")
    name = factory.Faker("bs")
    author = factory.Faker("name")
    description = factory.Faker("bs")
