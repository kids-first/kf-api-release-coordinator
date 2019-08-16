import factory

from coordinator.api.models.study import Study


class StudyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Study
        django_get_or_create = ("kf_id",)

    kf_id = "SD_TESTTEST"
    name = factory.Faker("bs")
    visible = factory.Faker("boolean")
