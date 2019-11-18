import pytest
from graphql_relay.node.node import to_global_id
from coordinator.api.models import ReleaseNote
from coordinator.api.factories.release_note import ReleaseNoteFactory


UPDATE_RELEASE_NOTE = """
mutation ($releaseNote: ID!, $input: UpdateReleaseNoteInput!) {
    updateReleaseNote(releaseNote: $releaseNote, input: $input) {
        releaseNote {
            id
            kfId
            uuid
            author
            description
            createdAt
            study {
                id
                kfId
            }
            release {
                id
                kfId
            }
        }
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [("admin", True), ("dev", True), ("user", False), ("anon", False)],
)
def test_update_release_note_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can update new release notes
    DEV - Can update new release notes
    USER - May not update relase notes
    anonomous - May not update release notes
    """
    release_note = ReleaseNoteFactory()
    release_note_id = to_global_id("ReleaseNoteNode", release_note.kf_id)

    variables = {
        "releaseNote": release_note_id,
        "input": {"description": "Test "},
    }

    client = test_client(user_type)
    resp = client.post(
        "/graphql",
        format="json",
        data={"query": UPDATE_RELEASE_NOTE, "variables": variables},
    )
    print(resp.json())

    if expected:
        assert (
            "kfId" in resp.json()["data"]["updateReleaseNote"]["releaseNote"]
        )
    else:
        assert "errors" in resp.json()


def test_update_release_note(db, admin_client):
    """
    Test that release notes are updated correctly.
    """
    release_note = ReleaseNoteFactory()
    release_note_id = to_global_id("ReleaseNoteNode", release_note.kf_id)

    variables = {
        "releaseNote": release_note_id,
        "input": {"description": "Updated description"},
    }
    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": UPDATE_RELEASE_NOTE, "variables": variables},
    )

    release = resp.json()["data"]["updateReleaseNote"]["releaseNote"]
    assert ReleaseNote.objects.count() == 1
    assert release["kfId"] == ReleaseNote.objects.first().kf_id
    assert release["description"] == variables["input"]["description"]


def test_update_release_note_not_found(db, admin_client):
    """
    Test that we may not update release notes that do not exist
    """
    release_note = ReleaseNoteFactory()
    release_note_id = to_global_id("ReleaseNoteNode", release_note.kf_id)
    release_note.delete()

    variables = {
        "releaseNote": release_note_id,
        "input": {"description": "Updated description"},
    }
    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": UPDATE_RELEASE_NOTE, "variables": variables},
    )

    assert "errors" in resp.json()
    errors = resp.json()["errors"]
    assert "does not exist" in errors[0]["message"]
