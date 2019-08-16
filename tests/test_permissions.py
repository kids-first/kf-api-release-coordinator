import time
import pytest

from coordinator.api.factories.task import TaskFactory


BASE_URL = "http://testserver"
SERVICE_URL = f"{BASE_URL}/task-services/"
RELEASE_URL = f"{BASE_URL}/releases/"


@pytest.mark.parametrize(
    "user_type,endpoint,method,status_code",
    [
        # admin
        ("admin", "/tasks", "get", 200),
        ("admin", "/tasks", "post", 201),
        ("admin", "/tasks/<kf_id>", "get", 200),
        ("admin", "/tasks/<kf_id>", "patch", 200),
        ("admin", "/tasks/<kf_id>", "put", 200),
        ("admin", "/tasks/<kf_id>", "delete", 405),
        # user
        ("user", "/tasks", "get", 200),
        ("user", "/tasks", "post", 403),
        ("user", "/tasks/<kf_id>", "get", 200),
        ("user", "/tasks/<kf_id>", "patch", 403),
        ("user", "/tasks/<kf_id>", "put", 403),
        ("user", "/tasks/<kf_id>", "delete", 403),
        # anon
        ("anon", "/tasks", "get", 200),
        ("anon", "/tasks", "post", 403),
        ("anon", "/tasks/<kf_id>", "get", 200),
        ("anon", "/tasks/<kf_id>", "patch", 403),
        ("anon", "/tasks/<kf_id>", "put", 403),
        ("anon", "/tasks/<kf_id>", "delete", 403),
    ],
)
@pytest.mark.django_db
def test_task_permissions(
    test_client, user_type, endpoint, method, status_code
):
    task = TaskFactory()
    endpoint = endpoint.replace("<kf_id>", task.kf_id)
    body = None
    if method in ["post", "patch", "put"]:
        body = {
            "progress": 30,
            "release": RELEASE_URL + task.release.kf_id,
            "task_service": SERVICE_URL + task.task_service.kf_id,
        }
    client = test_client(user_type)
    call = getattr(client, method)
    resp = call(endpoint, data=body)
    assert resp.status_code == status_code
