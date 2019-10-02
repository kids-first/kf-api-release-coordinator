import pytest
from graphql_relay.node.node import to_global_id
from coordinator.api.models import Release
from coordinator.api.factories.release import ReleaseFactory


PUBLISH_RELEASE = """
mutation ($release: ID!) {
    publishRelease(release: $release) {
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
    [("admin", True), ("dev", False), ("user", False), ("anon", False)],
)
def test_publish_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can publish a release
    DEV - May not publish a release
    USER - May not publish a relase
    anonomous - May not publish a release
    """
    release = ReleaseFactory(state="staged")
    variables = {"release": to_global_id("ReleaseNode", release.kf_id)}

    client = test_client(user_type)
    resp = client.post(
        "/graphql",
        format="json",
        data={"query": PUBLISH_RELEASE, "variables": variables},
    )

    if expected:
        assert "kfId" in resp.json()["data"]["publishRelease"]["release"]
    else:
        assert "errors" in resp.json()
        assert "Not authenticated" in resp.json()["errors"][0]["message"]


@pytest.mark.parametrize(
    "state,allowed",
    [
        ("waiting", False),
        ("initializing", False),
        ("running", False),
        ("staged", True),
        ("canceling", False),
        ("canceled", False),
        ("publishing", False),
        ("published", False),
    ],
)
def test_publish_release_from_state(db, admin_client, mocker, state, allowed):
    """
    Test that a release may only be published from the staged state.
    """
    mock_rq = mocker.patch("coordinator.graphql.releases.django_rq")

    release = ReleaseFactory(state=state)
    variables = {"release": to_global_id("ReleaseNode", release.kf_id)}

    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": PUBLISH_RELEASE, "variables": variables},
    )

    if allowed:
        # Check that the release task was queued
        assert mock_rq.enqueue.call_count == 1
        assert (
            resp.json()["data"]["publishRelease"]["release"]["state"]
            == "publishing"
        )
    else:
        assert "errors" in resp.json()
