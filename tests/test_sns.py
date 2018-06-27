import boto3
import json
import pytest
from mock import Mock, patch
from django.conf import settings
from coordinator.api.models import Release, Task, TaskService, Event


BASE_URL = 'http://testserver'


def test_new_release_event(admin_client, transactional_db, mocker):
    """ Test that createing a new release publishes to sns """
    arn = 'arn:aws:sns:us-east-1:538745987955:kf-coord-api-us-east-1-dev'
    settings.SNS_ARN = arn
    mock = mocker.patch('coordinator.api.models.boto3.client')
    assert Release.objects.count() == 0

    # Add an event to a task
    release = {
        'name': 'Test release',
        'description': 'Testing events',
        'studies': ['SD_00000000']
    }
    resp = admin_client.post(BASE_URL+'/releases', data=release)
    assert resp.status_code == 201
    assert Release.objects.count() == 1
    assert Event.objects.count() == 1
    assert mock().publish.call_count == 1
    message = {
        'default': json.dumps({
            'event_type': 'info',
            'message': 'release started',
            'task_service': None,
            'task': None,
            'release': Release.objects.first().kf_id
        })
    }
    arn = 'arn:aws:sns:us-east-1:538745987955:kf-coord-api-us-east-1-dev'
    mock().publish.assert_called_with(Message=json.dumps(message),
                                      MessageStructure='json',
                                      TopicArn=arn)
    settings.SNS_ARN = None


def test_new_general_event(client, transactional_db, mocker):
    """ Test that createing a new event publishes to sns """
    arn = 'arn:aws:sns:us-east-1:538745987955:kf-coord-api-us-east-1-dev'
    settings.SNS_ARN = arn
    mock = mocker.patch('coordinator.api.models.boto3.client')
    assert Event.objects.count() == 0

    ev = Event(event_type='error', message='test error event')
    ev.save()
    assert Event.objects.count() == 1
    assert mock().publish.call_count == 1
    message = {
        'default': json.dumps({
            'event_type': 'error',
            'message': 'test error event',
            'task_service': None,
            'task': None,
            'release': None
        })
    }
    arn = 'arn:aws:sns:us-east-1:538745987955:kf-coord-api-us-east-1-dev'
    mock().publish.assert_called_with(Message=json.dumps(message),
                                      MessageStructure='json',
                                      TopicArn=arn)
    settings.SNS_ARN = None


def test_no_arn(client, transactional_db, mocker):
    """ Test that no message is sent if there is no setting present """
    mock = mocker.patch('coordinator.api.models.boto3.client')
    assert Event.objects.count() == 0

    ev = Event(event_type='error', message='test error event')
    ev.save()

    assert Event.objects.count() == 1
    assert mock().publish.call_count == 0
