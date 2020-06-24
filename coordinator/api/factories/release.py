import factory
from factory.fuzzy import FuzzyChoice

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
    state = FuzzyChoice(
        ["waiting", "failed", "canceled", "staged", "rejected", "published"]
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
            study = StudyFactory(kf_id="SD_ME0WME0W")
            study = StudyFactory(kf_id="SD_W2PQV9FJ")
            study = StudyFactory(kf_id="SD_QQXC6C3V")
            study = StudyFactory(kf_id="SD_ODWXI1TE")
            self.studies.add(study)
