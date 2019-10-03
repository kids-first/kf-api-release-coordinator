import pytest
from graphql_relay.node.node import to_global_id
from coordinator.api.models import Release
from coordinator.api.factories.study import StudyFactory


CREATE_RELEASE = """
mutation ($input: ReleaseInput!) {
    startRelease(input: $input) {
        release {
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
            studies {
                edges {
                    node {
                        id
                        kfId
                    }
                }
            }
        }
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [("admin", True), ("dev", True), ("user", False), ("anon", False)],
)
def test_start_release_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can create a new release
    DEV - Can create a new release
    USER - May not create relases
    anonomous - May not create releases
    """
    studies = StudyFactory.create_batch(3)
    study_ids = [to_global_id("StudyNode", study.kf_id) for study in studies]

    variables = {
        "input": {
            "name": "Test Release",
            "isMajor": False,
            "studies": study_ids,
        }
    }

    client = test_client(user_type)
    resp = client.post(
        "/graphql",
        format="json",
        data={"query": CREATE_RELEASE, "variables": variables},
    )

    if expected:
        assert "kfId" in resp.json()["data"]["startRelease"]["release"]
    else:
        assert "errors" in resp.json()


def test_create_release(db, admin_client, mocker):
    """
    Test that releases are created correctly.
    """
    mock_rq = mocker.patch("coordinator.graphql.releases.django_rq")

    studies = StudyFactory.create_batch(3)
    study_ids = [to_global_id("StudyNode", study.kf_id) for study in studies]

    variables = {
        "input": {
            "name": "Test Release",
            "isMajor": False,
            "studies": study_ids,
        }
    }

    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": CREATE_RELEASE, "variables": variables},
    )

    release = resp.json()["data"]["startRelease"]["release"]
    assert release["kfId"] == Release.objects.first().kf_id
    assert release["name"] == "Test Release"
    assert release["isMajor"] is False
    assert release["author"] == "bobby"
    assert len(release["studies"]["edges"]) == 3

    # Check that the release task was queued
    assert mock_rq.enqueue.call_count == 1
