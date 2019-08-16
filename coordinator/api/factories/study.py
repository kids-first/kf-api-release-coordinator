import factory

from coordinator.api.models.study import Study


class StudyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Study

    kf_id = "SD_TESTTEST"
    name = factory.Faker("bs")
    visible = factory.Faker("boolean")
