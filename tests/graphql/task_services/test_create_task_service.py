import pytest
from graphql_relay.node.node import to_global_id
from coordinator.api.factories.study import StudyFactory


CREATE_SERVICE = """
mutation ($input: TaskServiceInput!) {
    createTaskService(input: $input) {
        taskService {
            id
            kfId
            uuid
            author
            name
            description
            createdAt
        }
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [("admin", True), ("dev", True), ("user", False), ("anon", False)],
)
def test_create_service_permissions(
    db, test_client, mocker, user_type, expected
):
    """
    ADMIN - Can create a new task service
    DEV - Can create a new task service
    USER - May not create new task services
    anonomous - May not create new task services
    """
    mock_validate = mocker.patch(
        "coordinator.graphql.task_services.validate_endpoint"
    )
    mock_validate.return_value = True

    variables = {
        "input": {"name": "Test Task Service", "url": "http://myservice"}
    }

    client = test_client(user_type)
    resp = client.post(
        "/graphql",
        format="json",
        data={"query": CREATE_SERVICE, "variables": variables},
    )

    if expected:
        assert (
            "kfId" in resp.json()["data"]["createTaskService"]["taskService"]
        )
    else:
        assert "errors" in resp.json()
