import pytest
from graphql_relay.node.node import to_global_id
from coordinator.api.models import Release
from coordinator.api.factories.release import ReleaseFactory


UPDATE_RELEASE = """
mutation ($release: ID!, $input: UpdateReleaseInput!) {
    updateRelease(release: $release, input: $input) {
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
def test_update_release_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can update a new release
    DEV - Can update a new release
    USER - May not update relases
    anonomous - May not update releases
    """
    release = ReleaseFactory()

    variables = {
        "release": to_global_id("ReleaseNode", release.kf_id),
        "input": {"name": "Edited Title"},
    }

    client = test_client(user_type)
    resp = client.post(
        "/graphql",
        format="json",
        data={"query": UPDATE_RELEASE, "variables": variables},
    )

    print(resp.json())
    if expected:
        assert "kfId" in resp.json()["data"]["updateRelease"]["release"]
    else:
        assert "errors" in resp.json()


def test_update_release(db, admin_client, mocker):
    """
    Test that releases are created correctly.
    """
    release = ReleaseFactory()

    variables = {
        "release": to_global_id("ReleaseNode", release.kf_id),
        "input": {
            "name": "Edited Title",
            "description": "Updated Description",
        },
    }

    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": UPDATE_RELEASE, "variables": variables},
    )

    release = resp.json()["data"]["updateRelease"]["release"]
    assert release["kfId"] == Release.objects.first().kf_id
    assert release["name"] == "Edited Title"
    assert release["description"] == "Updated Description"

    assert Release.objects.get(kf_id=release["kfId"]).name == "Edited Title"
