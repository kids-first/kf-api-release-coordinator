import pytest
from coordinator.api.models import Study, Task
from coordinator.api.factories.release import ReleaseFactory


ALL_TASKS = """
query (
    $state: String,
    $createdBefore: Float,
    $createdAfter: Float,
    $orderBy:String
) {
    allTasks(
        state: $state,
        createdBefore: $createdBefore,
        createdAfter: $createdAfter,
        orderBy: $orderBy
    ) {
        edges {
            node {
                id
                kfId
                uuid
                state
                createdAt
            }
        }
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [
        ("admin", lambda: 30),
        ("dev", lambda: 30),
        ("user", lambda: 10),
        ("anon", lambda: 10),
    ],
)
def test_list_all_tasks_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can query all tasks
    DEV - Can query all tasks
    USER - Can query tasks from published releases, or releases that they
           have a study in.
    anonomous - Can query tasks from published releases
    """
    study = Study(kf_id="SD_00000001")
    study.save()

    releases = ReleaseFactory.create_batch(10, state="staged")
    releases = ReleaseFactory.create_batch(10, state="published")
    releases = ReleaseFactory.create_batch(
        10, state="staging", studies=[study]
    )

    client = test_client(user_type)
    resp = client.post("/graphql", data={"query": ALL_TASKS})
    # Test that the correct number of releases are returned
    assert len(resp.json()["data"]["allTasks"]["edges"]) == expected()
