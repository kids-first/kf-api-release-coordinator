import pytest
from coordinator.api.models import ReleaseNote
from coordinator.api.factories.release import ReleaseFactory
from coordinator.api.factories.release_note import ReleaseNoteFactory
from coordinator.api.factories.study import StudyFactory


ALL_RELEASE_NOTES = """
query (
    $author: String,
    $study: ID,
    $release: ID,
    $createdBefore: Float,
    $createdAfter: Float,
    $orderBy:String
) {
    allReleaseNotes(
        author: $author,
        study: $study,
        release: $release,
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
                description
                createdAt
            }
        }
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [("admin", 30), ("dev", 30), ("user", 20), ("anon", 10)],
)
def test_list_all_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can query all release notes
    DEV - Can query all release notes
    USER - Can query release notes from published releases and releases that
        their studies are in
    ANON - Can only query release notes from published release notes
    """
    study = StudyFactory(kf_id="SD_00000001")
    release_study = ReleaseFactory(state="staging", studies=[study])
    release_staged = ReleaseFactory(state="staged")
    release_pub = ReleaseFactory(state="published")

    release_notes = ReleaseNoteFactory.create_batch(10, release=release_staged)
    releases_notes = ReleaseNoteFactory.create_batch(10, release=release_pub)
    releases_notes = ReleaseNoteFactory.create_batch(
        10, release=release_study, study=study
    )

    client = test_client(user_type)
    resp = client.post("/graphql", data={"query": ALL_RELEASE_NOTES})
    # Test that the correct number of release notes are returned
    assert len(resp.json()["data"]["allReleaseNotes"]["edges"]) == expected
