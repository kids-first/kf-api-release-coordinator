import pytest
from coordinator.api.models import Study, Task
from coordinator.api.factories.release import ReleaseFactory


ALL_TASK_SERVICES = """
query (
    $name: String,
    $url: String,
    $author: String,
    $createdBefore: Float,
    $createdAfter: Float,
    $orderBy:String
) {
    allTaskServices(
        name: $name,
        url: $url,
        author: $author,
        createdBefore: $createdBefore,
        createdAfter: $createdAfter,
        orderBy: $orderBy
    ) {
        edges {
            node {
                id
                kfId
                uuid
                author
                name
                description
                url
                enabled
                createdAt
            }
        }
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [
        ("admin", lambda: 3),
        ("dev", lambda: 3),
        ("user", lambda: 0),
        ("anon", lambda: 0),
    ],
)
def test_list_all_tasks_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can query all task services
    DEV - Can query all task services
    USER - Cannot query any task services
    anonomous - Cannot query any task services

    The TaskServiceFactory maxes at 3 unique task services, so we should never
    expect more than than.
    """
    study = Study(kf_id="SD_00000001")
    study.save()

    releases = ReleaseFactory.create_batch(10, state="staged")
    releases = ReleaseFactory.create_batch(10, state="published")
    releases = ReleaseFactory.create_batch(
        10, state="staging", studies=[study]
    )

    client = test_client(user_type)
    resp = client.post("/graphql", data={"query": ALL_TASK_SERVICES})
    # Test that the correct number of releases are returned
    assert len(resp.json()["data"]["allTaskServices"]["edges"]) == expected()
