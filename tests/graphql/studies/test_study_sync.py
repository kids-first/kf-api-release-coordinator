import pytest


SYNC_STUDIES = """
mutation {
    syncStudies {
    new {
      edges {
        node {
          id
          kfId
        }
      }
    }
    deleted {
      edges {
        node {
          id
          kfId
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
def test_sync_permissions(db, test_client, mocker, user_type, expected):
    """
    ADMIN - Can sync studies
    DEV - Can sync studies
    USER - Can not sync studies
    anonomous - Can not sync studies
    """
    mock_sync = mocker.patch("coordinator.graphql.studies.sync")
    mock_sync.return_value = [], []

    client = test_client(user_type)
    resp = client.post("/graphql", data={"query": SYNC_STUDIES})

    assert "errors" in resp.json() if not expected else "data" in resp.json()
    assert mock_sync.call_count == 1 if expected else mock_sync.call_count == 0
