import pytest
from coordinator.api.models import Release
from coordinator.api.factories.release import ReleaseFactory


ALL_RELEASES = """
query (
    $version: String,
    $state: String,
    $author: String,
    $name: String,
    $isMajor: Boolean,
    $nameContains: String,
    $createdBefore: Float,
    $createdAfter: Float,
    $orderBy:String
) {
    allReleases(
        version: $version,
        state: $state,
        author: $author,
        name: $name,
        isMajor: $isMajor,
        nameContains: $nameContains,
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
                state
                tags
                version
                isMajor
                createdAt
            }
        }
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [("admin", 20), ("dev", 20), ("user", 10), ("anon", 10)],
)
def test_list_all_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can query all releases
    DEV - Can query all releases
    USER - Can query published releases and releases that their studies are in
    anonomous - Can only query published releases
    """

    releases = ReleaseFactory.create_batch(10, state='staged')
    releases = ReleaseFactory.create_batch(10, state='published')

    client = test_client(user_type)
    resp = client.post("/graphql", data={"query": ALL_RELEASES})
    # Test that the correct number of releases are returned
    assert len(resp.json()["data"]["allReleases"]["edges"]) == expected
