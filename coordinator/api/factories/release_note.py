import factory

from coordinator.api.models.release_note import ReleaseNote
from coordinator.api.factories.study import StudyFactory
from coordinator.api.factories.release import ReleaseFactory


class ReleaseNoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReleaseNote

    kf_id = "RN_00000000"
    author = factory.Faker("name")
    description = factory.Faker("bs")
    study = factory.SubFactory(StudyFactory)
    release = factory.SubFactory(ReleaseFactory, kf_id="RE_00000000")
