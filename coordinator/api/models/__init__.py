import boto3
import json

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_fsm.signals import post_transition

from coordinator.api.models.task import Task, task_id
from coordinator.api.models.taskservice import TaskService, task_service_id
from coordinator.api.models.release import Release, release_id
from coordinator.api.models.event import Event, event_id
from coordinator.api.models.study import Study


@receiver(post_transition, sender=Release)
def create_release_event(sender, instance, name, source, target, **kwargs):
    ev_type = 'error' if target in ['failed', 'rejected'] else 'info'
    ev = Event(event_type=ev_type,
               message='release {}, version {} changed from {} to {}'
                       .format(instance.kf_id, instance.version,
                               source, target),
               release=instance)
    ev.save()


@receiver(post_transition, sender=Task)
def create_task_event(sender, instance, name, source, target, **kwargs):
    ev_type = 'error' if target in ['failed', 'rejected'] else 'info'
    ev = Event(event_type=ev_type,
               message='task {} changed from {} to {}'
                       .format(instance.kf_id, source, target),
               release=instance.release,
               task=instance,
               task_service=instance.task_service)
    ev.save()


@receiver(post_save, sender=Event)
def send_sns(sender, instance, **kwargs):
    if settings.SNS_ARN is not None:
        client = boto3.client('sns')
        message = {
            'default': {
                'event_type': instance.event_type,
                'message': instance.message,
                'task_service': None,
                'task': None,
                'release': None
            }
        }
        if instance.task_service:
            message['default']['task_service'] = instance.task_service.kf_id
        if instance.task:
            message['default']['task'] = instance.task.kf_id
        if instance.release:
            message['default']['release'] = instance.release.kf_id

        message['default'] = json.dumps(message['default'])

        client.publish(TopicArn=settings.SNS_ARN,
                       MessageStructure='json',
                       Message=json.dumps(message))
