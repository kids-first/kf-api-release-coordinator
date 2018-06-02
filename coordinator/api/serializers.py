from coordinator.api.models import Task, TaskService, Release, Event
from rest_framework import serializers
from coordinator.api.validators import validate_study


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    service_name = serializers.CharField(read_only=True,
                                         source='task_service.name')

    class Meta:
        model = Task
        fields = ('kf_id', 'state', 'progress', 'release', 'task_service',
                  'created_at', 'service_name')
        read_only_fields = ('kf_id', 'created_at')
        extra_kwargs = {
            'release': {'allow_null': False, 'lookup_field': 'kf_id'},
            'task_service': {'allow_null': False, 'lookup_field': 'kf_id'},
        }


class TaskServiceSerializer(serializers.HyperlinkedModelSerializer):
    tasks = TaskSerializer(read_only=True, many=True)

    class Meta:
        model = TaskService
        fields = ('kf_id', 'name', 'description', 'last_ok_status', 'author',
                  'health_status', 'url', 'tasks', 'created_at', 'enabled')
        read_only_fields = ('kf_id', 'last_ok_status', 'health_status',
                            'created_at')


class ReleaseSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.ListField(
                child=serializers.CharField(max_length=50, allow_blank=False,
                                            validators=[]))
    studies = serializers.ListField(
                child=serializers.CharField(max_length=11, allow_blank=False,
                                            validators=[validate_study]),
                min_length=1)
    tasks = TaskSerializer(read_only=True, many=True)

    class Meta:
        model = Release
        fields = ('kf_id', 'name', 'description', 'state', 'studies',
                  'tasks', 'created_at', 'tags', 'author')
        read_only_fields = ('kf_id', 'state', 'tasks', 'created_at')


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('kf_id', 'event_type', 'message', 'release', 'task_service',
                  'task', 'created_at')
        read_only_fields = ('kf_id', 'created_at')
        extra_kwargs = {
            'release': {'allow_null': True, 'lookup_field': 'kf_id'},
            'task_service': {'allow_null': True, 'lookup_field': 'kf_id'},
            'task': {'allow_null': True, 'lookup_field': 'kf_id'},
        }
