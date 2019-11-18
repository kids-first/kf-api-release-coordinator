import pytest
from graphql_relay.node.node import to_global_id
from coordinator.api.models import ReleaseNote
from coordinator.api.factories.study import StudyFactory
from coordinator.api.factories.release import ReleaseFactory


CREATE_RELEASE_NOTE = """
mutation ($input: ReleaseNoteInput!) {
    createReleaseNote(input: $input) {
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
def test_create_release_note_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can create new release notes
    DEV - Can create new release notes
    USER - May not create relase notes
    anonomous - May not create release notes
    """
    study = StudyFactory()
    study_id = to_global_id("StudyNode", study.kf_id)
    release = ReleaseFactory(studies=[study])
    release_id = to_global_id("ReleaseNode", release.kf_id)

    variables = {
        "input": {
            "description": "Test note",
            "study": study_id,
            "release": release_id,
        }
    }

    client = test_client(user_type)
    resp = client.post(
        "/graphql",
        format="json",
        data={"query": CREATE_RELEASE_NOTE, "variables": variables},
    )

    if expected:
        assert (
            "kfId" in resp.json()["data"]["createReleaseNote"]["releaseNote"]
        )
    else:
        assert "errors" in resp.json()


def test_create_release_note(db, admin_client):
    """
    Test that releases are created correctly.
    """
    study = StudyFactory()
    study_id = to_global_id("StudyNode", study.kf_id)
    release = ReleaseFactory(studies=[study])
    release_id = to_global_id("ReleaseNode", release.kf_id)

    variables = {
        "input": {
            "description": "Test note",
            "study": study_id,
            "release": release_id,
        }
    }

    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": CREATE_RELEASE_NOTE, "variables": variables},
    )

    release = resp.json()["data"]["createReleaseNote"]["releaseNote"]
    assert ReleaseNote.objects.count() == 1
    assert release["kfId"] == ReleaseNote.objects.first().kf_id
    assert release["author"] == "bobby"


@pytest.mark.parametrize("entity", ["study", "release"])
def test_create_release_note_not_exist(db, admin_client, entity):
    """
    Test that release notes may only be made for entities that exist
    """
    study = StudyFactory()
    study_id = to_global_id("StudyNode", study.kf_id)
    release = ReleaseFactory(studies=[study])
    release_id = to_global_id("ReleaseNode", release.kf_id)

    if entity == "study":
        study.delete()
    if entity == "release":
        release.delete()

    variables = {
        "input": {
            "description": "Test note",
            "study": study_id,
            "release": release_id,
        }
    }

    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": CREATE_RELEASE_NOTE, "variables": variables},
    )

    assert "errors" in resp.json()
    error = resp.json()["errors"]
    assert "does not exist" in error[0]["message"]


def test_create_release_note_study_not_in_release(db, admin_client):
    """
    Test that notes may only be created for releases that contain the desired
    study
    """
    study = StudyFactory()
    study_id = to_global_id("StudyNode", study.kf_id)
    # The release will not contain the above study
    release = ReleaseFactory()
    release_id = to_global_id("ReleaseNode", release.kf_id)

    variables = {
        "input": {
            "description": "Test note",
            "study": study_id,
            "release": release_id,
        }
    }

    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": CREATE_RELEASE_NOTE, "variables": variables},
    )

    assert "errors" in resp.json()
    error = resp.json()["errors"]
    assert "is not in release" in error[0]["message"]
