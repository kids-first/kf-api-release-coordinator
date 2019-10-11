import pytest
from graphql_relay.node.node import to_global_id
from coordinator.api.models import TaskService
from coordinator.api.factories.study import StudyFactory


UPDATE_SERVICE = """
mutation UpdateTaskService($taskService: ID!, $input: TaskServiceInput!) {
    updateTaskService(taskService: $taskService, input: $input) {
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
def test_update_service_permissions(
    db, test_client, mocker, user_type, expected
):
    """
    ADMIN - Can update a new task service
    DEV - Can update a new task service
    USER - May not update new task services
    anonomous - May not update new task services
    """
    mock_validate = mocker.patch(
        "coordinator.graphql.task_services.validate_endpoint"
    )
    mock_validate.return_value = True

    service = TaskService(name="Test Service")
    service.save()
    relay_id = to_global_id("TaskServiceNode", service.kf_id)

    variables = {
        "taskService": relay_id,
        "input": {"name": "Test Task Service", "url": "TEST"},
    }

    client = test_client(user_type)
    resp = client.post(
        "/graphql",
        format="json",
        data={"query": UPDATE_SERVICE, "variables": variables},
    )

    if expected:
        assert (
            "kfId" in resp.json()["data"]["updateTaskService"]["taskService"]
        )
    else:
        assert "errors" in resp.json()
