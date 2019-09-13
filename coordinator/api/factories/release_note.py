import factory

from coordinator.api.models.release_note import ReleaseNote
from coordinator.api.factories.study import StudyFactory
from coordinator.api.factories.release import ReleaseFactory


class ReleaseNoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReleaseNote

    kf_id = factory.Sequence(lambda n: f"RN_{n:08}")
    author = factory.Faker("name")
    description = factory.Faker("bs")
    release = factory.SubFactory(ReleaseFactory)
    study = factory.SubFactory(StudyFactory)
