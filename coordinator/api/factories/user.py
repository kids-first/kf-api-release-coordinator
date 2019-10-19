import factory

from coordinator.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    sub = factory.Faker("uuid4")
    username = factory.Faker("name")
    auth_groups = []
    auth_roles = []
