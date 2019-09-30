import pytest
from coordinator.api.models import Study
from coordinator.api.factories.study import StudyFactory


ALL_STUDIES = """
query (
    $kfId: String,
    $visible: Boolean,
    $deleted: Boolean,
    $nameContains: String,
    $createdBefore: Float,
    $createdAfter: Float,
    $orderBy: String
) {
    allStudies(
        kfId: $kfId,
        visible: $visible,
        deleted: $deleted,
        nameContains: $nameContains,
        createdBefore: $createdBefore,
        createdAfter: $createdAfter,
        orderBy: $orderBy
    ) {
        edges {
            node {
                id
                kfId
                name
                visible
                deleted
                createdAt
            }
        }
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [("admin", 40), ("dev", 40), ("user", 10), ("anon", 10)],
)
def test_list_all_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can query all studies
    DEV - Can query all studies
    USER - Can query all non-deleted, visible studies
    anonomous - Can query all non-deleted, visible studies
    """

    studies = StudyFactory.create_batch(10, visible=True)
    studies = StudyFactory.create_batch(10, visible=False)
    studies = StudyFactory.create_batch(10, deleted=True)
    studies = StudyFactory.create_batch(10, visible=True, deleted=True)

    client = test_client(user_type)
    resp = client.post("/graphql", data={"query": ALL_STUDIES})
    # Test that the correct number of releases are returned
    assert len(resp.json()["data"]["allStudies"]["edges"]) == expected
