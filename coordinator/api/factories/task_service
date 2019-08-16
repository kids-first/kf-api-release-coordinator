import factory

from coordinator.api.models.release import Release


class ReleaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Release

    name = factory.Faker("bs")
    author = factory.Faker("name")
    description = factory.Faker("bs")
