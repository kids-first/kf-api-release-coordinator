import factory

from coordinator.api.models.release import Release
from coordinator.api.factories.study import StudyFactory


class ReleaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Release

    name = factory.Faker("bs")
    author = factory.Faker("name")
    description = factory.Faker("bs")
    tasks = factory.RelatedFactory(
        "coordinator.api.factories.task.TaskFactory", "release"
    )

    @factory.post_generation
    def studies(self, create, extracted, **kwargs):
        if not create:
            self.studies.add(StudyFactory())
            return

        if extracted:
            for study in extracted:
                self.studies.add(study)
        else:
            study = StudyFactory(kf_id="SD_TESTTEST")
            self.studies.add(study)
