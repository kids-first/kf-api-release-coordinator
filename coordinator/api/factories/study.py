import factory

from coordinator.api.models.study import Study


class StudyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Study
        django_get_or_create = ("kf_id",)

    # kf_id = "SD_TESTTEST"
    kf_id = factory.Sequence(lambda n: f"SD_{n:08}")
    name = factory.Faker("bs")
    visible = factory.Faker("boolean")
