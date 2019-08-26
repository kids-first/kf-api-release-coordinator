import time
import pytest
from mock import Mock

from coordinator.api.factories.task import TaskFactory
from coordinator.api.factories.task_service import TaskServiceFactory
from coordinator.api.factories.release import ReleaseFactory
from coordinator.api.factories.release_note import ReleaseNoteFactory
from coordinator.api.factories.study import StudyFactory


BASE_URL = "http://testserver"
SERVICE_URL = f"{BASE_URL}/task-services/"
RELEASE_URL = f"{BASE_URL}/releases/"
STUDY_URL = f"{BASE_URL}/studies/"


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
        ("user", "/tasks/<kf_id>", "patch", 200),  # TODO: This shouldn't be ok
        ("user", "/tasks/<kf_id>", "put", 403),
        ("user", "/tasks/<kf_id>", "delete", 403),
        # anon
        ("anon", "/tasks", "get", 200),
        ("anon", "/tasks", "post", 403),
        ("anon", "/tasks/<kf_id>", "get", 200),
        ("anon", "/tasks/<kf_id>", "patch", 200),  # TODO: This shouldn't be ok
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


@pytest.mark.parametrize(
    "user_type,endpoint,method,status_code",
    [
        # admin
        ("admin", "/releases", "get", 200),
        ("admin", "/releases", "post", 201),
        ("admin", "/releases/<kf_id>", "get", 200),
        ("admin", "/releases/<kf_id>", "patch", 200),
        ("admin", "/releases/<kf_id>", "put", 200),
        ("admin", "/releases/<kf_id>", "delete", 200),
        # user
        ("user", "/releases", "get", 200),
        ("user", "/releases", "post", 403),
        ("user", "/releases/<kf_id>", "get", 200),
        ("user", "/releases/<kf_id>", "patch", 403),
        ("user", "/releases/<kf_id>", "put", 403),
        ("user", "/releases/<kf_id>", "delete", 403),
        # anon
        ("anon", "/releases", "get", 200),
        ("anon", "/releases", "post", 403),
        ("anon", "/releases/<kf_id>", "get", 200),
        ("anon", "/releases/<kf_id>", "patch", 403),
        ("anon", "/releases/<kf_id>", "put", 403),
        ("anon", "/releases/<kf_id>", "delete", 403),
    ],
)
@pytest.mark.django_db
def test_release_permissions(
    test_client, user_type, endpoint, method, status_code
):
    release = ReleaseFactory()
    endpoint = endpoint.replace("<kf_id>", release.kf_id)
    body = None
    if method in ["post", "patch", "put"]:
        body = {
            "name": release.name,
            "description": release.description,
            "studies": [release.studies.first().kf_id],
        }
    client = test_client(user_type)
    call = getattr(client, method)
    resp = call(endpoint, data=body)
    assert resp.status_code == status_code


@pytest.mark.parametrize(
    "user_type,endpoint,method,status_code",
    [
        # admin
        ("admin", "/release-notes", "get", 200),
        ("admin", "/release-notes", "post", 201),
        ("admin", "/release-notes/<kf_id>", "get", 200),
        ("admin", "/release-notes/<kf_id>", "patch", 200),
        ("admin", "/release-notes/<kf_id>", "put", 200),
        ("admin", "/release-notes/<kf_id>", "delete", 204),
        # user
        ("user", "/release-notes", "get", 200),
        ("user", "/release-notes", "post", 403),
        ("user", "/release-notes/<kf_id>", "get", 200),
        ("user", "/release-notes/<kf_id>", "patch", 403),
        ("user", "/release-notes/<kf_id>", "put", 403),
        ("user", "/release-notes/<kf_id>", "delete", 403),
        # anon
        ("anon", "/release-notes", "get", 200),
        ("anon", "/release-notes", "post", 403),
        ("anon", "/release-notes/<kf_id>", "get", 200),
        ("anon", "/release-notes/<kf_id>", "patch", 403),
        ("anon", "/release-notes/<kf_id>", "put", 403),
        ("anon", "/release-notes/<kf_id>", "delete", 403),
    ],
)
@pytest.mark.django_db
def test_release_note_permissions(
    test_client, user_type, endpoint, method, status_code
):
    note = ReleaseNoteFactory()
    endpoint = endpoint.replace("<kf_id>", note.kf_id)
    body = None
    if method in ["post", "patch", "put"]:
        body = {
            "description": "testing",
            "author": "me",
            "study": STUDY_URL + note.study.kf_id,
            "release": RELEASE_URL + note.release.kf_id,
        }
    client = test_client(user_type)
    call = getattr(client, method)
    resp = call(endpoint, data=body)
    assert resp.status_code == status_code


@pytest.mark.parametrize(
    "user_type,endpoint,method,status_code",
    [
        # admin
        ("admin", "/studies", "get", 200),
        ("admin", "/studies", "post", 405),
        ("admin", "/studies/<kf_id>", "get", 200),
        ("admin", "/studies/<kf_id>", "patch", 405),
        ("admin", "/studies/<kf_id>", "put", 405),
        ("admin", "/studies/<kf_id>", "delete", 405),
        # user
        ("user", "/studies", "get", 200),
        ("user", "/studies", "post", 405),
        ("user", "/studies/<kf_id>", "get", 200),
        ("user", "/studies/<kf_id>", "patch", 405),
        ("user", "/studies/<kf_id>", "put", 405),
        ("user", "/studies/<kf_id>", "delete", 405),
        # anon
        ("anon", "/studies", "get", 200),
        ("anon", "/studies", "post", 405),
        ("anon", "/studies/<kf_id>", "get", 200),
        ("anon", "/studies/<kf_id>", "patch", 405),
        ("anon", "/studies/<kf_id>", "put", 405),
        ("anon", "/studies/<kf_id>", "delete", 405),
    ],
)
@pytest.mark.django_db
def test_study_permissions(
    test_client, user_type, endpoint, method, status_code
):
    study = StudyFactory(kf_id="SD_TESTTEST")
    endpoint = endpoint.replace("<kf_id>", study.kf_id)
    body = None
    if method in ["post", "patch", "put"]:
        body = {"name": study.name}
    client = test_client(user_type)
    call = getattr(client, method)
    resp = call(endpoint, data=body)
    assert resp.status_code == status_code


@pytest.mark.parametrize(
    "user_type,endpoint,method,status_code",
    [
        # admin
        ("admin", "/task-services", "get", 200),
        ("admin", "/task-services", "post", 201),
        ("admin", "/task-services/<kf_id>", "get", 200),
        ("admin", "/task-services/<kf_id>", "patch", 200),
        ("admin", "/task-services/<kf_id>", "put", 200),
        ("admin", "/task-services/<kf_id>", "delete", 204),
        # user
        ("user", "/task-services", "get", 200),
        ("user", "/task-services", "post", 403),
        ("user", "/task-services/<kf_id>", "get", 200),
        ("user", "/task-services/<kf_id>", "patch", 403),
        ("user", "/task-services/<kf_id>", "put", 403),
        ("user", "/task-services/<kf_id>", "delete", 403),
        # anon
        ("anon", "/task-services", "get", 200),
        ("anon", "/task-services", "post", 403),
        ("anon", "/task-services/<kf_id>", "get", 200),
        ("anon", "/task-services/<kf_id>", "patch", 403),
        ("anon", "/task-services/<kf_id>", "put", 403),
        ("anon", "/task-services/<kf_id>", "delete", 403),
    ],
)
@pytest.mark.django_db
def test_task_service_permissions(
    mocker, test_client, user_type, endpoint, method, status_code
):
    mock_requests = mocker.patch("coordinator.api.validators.requests")
    mock_resp = Mock()
    mock_resp.content = str.encode('{"name": "test"}')
    mock_resp.status_code = 200
    mock_requests.get.return_value = mock_resp

    service = TaskServiceFactory()
    endpoint = endpoint.replace("<kf_id>", service.kf_id)
    body = None
    if method in ["post", "patch", "put"]:
        body = {
            "name": "My service",
            "description": "testing",
            "author": "me",
            "url": "http://test",
        }
    client = test_client(user_type)
    call = getattr(client, method)
    resp = call(endpoint, data=body)
    assert resp.status_code == status_code


@pytest.mark.parametrize(
    "user_type,endpoint,method,status_code",
    [
        # admin
        ("admin", "/releases/status_checks", "post", 200),
        ("admin", "/tasks/status_checks", "post", 200),
        # user
        ("user", "/releases/status_checks", "post", 200),
        ("user", "/tasks/status_checks", "post", 200),
        # anon
        ("anon", "/releases/status_checks", "post", 200),
        ("anon", "/tasks/status_checks", "post", 200),
    ],
)
@pytest.mark.django_db
def test_status_permissions(
    mocker, test_client, user_type, endpoint, method, status_code
):
    mock_requests = mocker.patch("coordinator.api.validators.requests")
    mock_resp = Mock()
    mock_resp.content = str.encode('{"name": "test"}')
    mock_resp.status_code = 200
    mock_requests.get.return_value = mock_resp

    service = TaskServiceFactory()
    endpoint = endpoint.replace("<kf_id>", service.kf_id)
    client = test_client(user_type)
    call = getattr(client, method)
    resp = call(endpoint)
    assert resp.status_code == status_code
