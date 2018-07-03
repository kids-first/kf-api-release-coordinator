import boto3
import json
import pytest
from mock import Mock, patch
from django.conf import settings
from coordinator.api.models import Release, Task, TaskService, Event


BASE_URL = 'http://testserver'


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
