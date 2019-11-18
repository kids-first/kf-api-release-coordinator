import pytest
from graphql_relay.node.node import to_global_id
from coordinator.api.models import ReleaseNote
from coordinator.api.factories.release_note import ReleaseNoteFactory


REMOVE_RELEASE_NOTE = """
mutation ($releaseNote: ID!) {
    removeReleaseNote(releaseNote: $releaseNote) {
        success
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [("admin", True), ("dev", True), ("user", False), ("anon", False)],
)
def test_remove_release_note_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can remove new release notes
    DEV - Can remove new release notes
    USER - May not remove relase notes
    anonomous - May not remove release notes
    """
    release_note = ReleaseNoteFactory()
    release_note_id = to_global_id("ReleaseNoteNode", release_note.kf_id)

    variables = {"releaseNote": release_note_id}

    client = test_client(user_type)
    resp = client.post(
        "/graphql",
        format="json",
        data={"query": REMOVE_RELEASE_NOTE, "variables": variables},
    )
    print(resp.json())

    if expected:
        assert resp.json()["data"]["removeReleaseNote"]["success"]
        with pytest.raises(ReleaseNote.DoesNotExist):
            ReleaseNote.objects.get(kf_id=release_note.kf_id)
    else:
        assert "errors" in resp.json()


def test_remove_release_note_not_found(db, admin_client):
    """
    Test that we may not remove release notes that do not exist
    """
    release_note = ReleaseNoteFactory()
    release_note_id = to_global_id("ReleaseNoteNode", release_note.kf_id)
    release_note.delete()

    variables = {"releaseNote": release_note_id}
    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": REMOVE_RELEASE_NOTE, "variables": variables},
    )

    assert "errors" in resp.json()
    errors = resp.json()["errors"]
    assert "does not exist" in errors[0]["message"]
