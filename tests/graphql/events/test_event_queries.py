import pytest
from coordinator.api.models import Study, Task
from coordinator.api.factories.release import ReleaseFactory
from coordinator.api.factories.study import StudyFactory
from coordinator.api.factories.event import EventFactory


ALL_EVENTS = """
query (
    $messageContains: String,
    $createdBefore: Float,
    $createdAfter: Float,
    $orderBy:String
) {
    allEvents(
        messageContains: $messageContains,
        createdBefore: $createdBefore,
        createdAfter: $createdAfter,
        orderBy: $orderBy
    ) {
        edges {
            node {
                id
                kfId
                uuid
                createdAt
                eventType
            }
        }
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [
        ("admin", lambda: 25),
        ("dev", lambda: 25),
        ("user", lambda: 15),
        ("anon", lambda: 10),
    ],
)
def test_list_all_events_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can query all events
    DEV - Can query all events
    USER - Can query all events for releases that have been published or which
        contain a study that the user is in the group of
    anonomous - Can query all events for releases that have been published
    """
    release_pub = ReleaseFactory(state="published")
    EventFactory.create_batch(10, release=release_pub)
    release_staged = ReleaseFactory(state="staged")
    EventFactory.create_batch(10, release=release_staged)
    study = StudyFactory(kf_id="SD_00000001")
    release_user = ReleaseFactory(state="staged", studies=[study])
    EventFactory.create_batch(5, release=release_user)

    client = test_client(user_type)
    resp = client.post("/graphql", data={"query": ALL_EVENTS})
    # Test that the correct number of releases are returned
    assert len(resp.json()["data"]["allEvents"]["edges"]) == expected()
