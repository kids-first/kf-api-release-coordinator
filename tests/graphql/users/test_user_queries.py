import pytest
from coordinator.api.factories.user import UserFactory


ALL_USERS = """
query (
    $username: String,
    $joinedBefore: Float,
    $joinedAfter: Float,
    $orderBy:String
) {
    allUsers(
        username: $username,
        joinedBefore: $joinedBefore,
        joinedAfter: $joinedAfter,
        orderBy: $orderBy
    ) {
        edges {
            node {
                id
                email
                username
                roles
                groups
                dateJoined
            }
        }
    }
}
"""

MY_PROFILE = """
query myProfile {
    myProfile {
        id
        email
        username
        roles
        groups
        dateJoined
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [
        ("admin", lambda: 11),
        ("dev", lambda: 11),
        ("user", lambda: 1),
        ("anon", lambda: 0),
    ],
)
def test_list_all_users_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can query all users
    DEV - Can query all users
    USER - Cannot query any users but self
    anonomous - Cannot query users
    """
    Users = UserFactory.create_batch(10)

    client = test_client(user_type)
    resp = client.post("/graphql", data={"query": ALL_USERS})
    # Test that the correct number of releases are returned
    assert len(resp.json()["data"]["allUsers"]["edges"]) == expected()


@pytest.mark.parametrize(
    "user_type,expected",
    [("admin", True), ("dev", True), ("user", True), ("anon", False)],
)
def test_list_my_profile_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can query all users
    DEV - Can query all users
    USER - Cannot query any users but self
    anonomous - Cannot query users
    """
    Users = UserFactory.create_batch(10)

    client = test_client(user_type)
    resp = client.post("/graphql", data={"query": MY_PROFILE})
    # Test that the correct number of releases are returned
    assert "errors" not in resp.json() if expected else "errors" in resp.json()
