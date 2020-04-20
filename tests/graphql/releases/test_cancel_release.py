import pytest
from graphql_relay.node.node import to_global_id
from coordinator.api.models import Release
from coordinator.api.factories.release import ReleaseFactory


CANCEL_RELEASE = """
mutation ($release: ID!) {
    cancelRelease(release: $release) {
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
def test_cancel_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can cancel a release
    DEV - Can cancel a release
    USER - May not cancel relases
    anonomous - May not cancel releases
    """
    release = ReleaseFactory(state="running")
    variables = {"release": to_global_id("ReleaseNode", release.kf_id)}

    client = test_client(user_type)
    resp = client.post(
        "/graphql",
        format="json",
        data={"query": CANCEL_RELEASE, "variables": variables},
    )

    if expected:
        assert "kfId" in resp.json()["data"]["cancelRelease"]["release"]
    else:
        assert "errors" in resp.json()
        assert "Not authenticated" in resp.json()["errors"][0]["message"]


@pytest.mark.parametrize(
    "state,allowed",
    [
        ("waiting", True),
        ("initializing", True),
        ("running", True),
        ("staged", True),
        ("canceling", True),
        ("canceled", False),
        ("publishing", True),
        ("published", False),
    ],
)
def test_cancel_release_from_state(db, admin_client, mocker, state, allowed):
    """
    Test that a release is canceled correctly from any state
    """
    mock_rq = mocker.patch("coordinator.graphql.releases.django_rq")

    release = ReleaseFactory(state=state)
    variables = {"release": to_global_id("ReleaseNode", release.kf_id)}

    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": CANCEL_RELEASE, "variables": variables},
    )

    if allowed:
        # Check that the release task was queued
        assert mock_rq.enqueue.call_count == 1
        assert (
            resp.json()["data"]["cancelRelease"]["release"]["state"]
            == "canceling"
        )
    else:
        assert "errors" in resp.json()
