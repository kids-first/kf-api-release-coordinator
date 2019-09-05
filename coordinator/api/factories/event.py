import factory
import factory.fuzzy

from coordinator.api.models.event import Event, EVENTS
from coordinator.api.factories.study import StudyFactory
from coordinator.api.factories.task import TaskFactory
from coordinator.api.factories.release import ReleaseFactory


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event
        django_get_or_create = ("kf_id",)

    kf_id = factory.Sequence(lambda n: f"SD_{n:08}")
    event_type = factory.fuzzy.FuzzyChoice(EVENTS, getter=lambda c: c[0])
    message = factory.Faker("bs")
    task = factory.SubFactory(TaskFactory)
    release = factory.SubFactory(ReleaseFactory)
