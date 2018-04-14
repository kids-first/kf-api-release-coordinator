from coordinator.api.models import Task, TaskService, Release
from rest_framework import serializers
from coordinator.api.validators import validate_study


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ('kf_id', 'state', 'progress', 'release', 'task_service',
                  'created_at')
        read_only_fields = ('kf_id', 'created_at')
        extra_kwargs = {
            'release': {'allow_null': False, 'lookup_field': 'kf_id'},
            'task_service': {'allow_null': False, 'lookup_field': 'kf_id'},
        }


class TaskServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaskService
        fields = ('kf_id', 'name', 'last_ok_status', 'health_status',
                  'url', 'created_at')
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

    class Meta:
        model = Release
        fields = ('kf_id', 'name', 'description', 'state', 'studies',
                  'created_at', 'tags', 'author')
        read_only_fields = ('kf_id', 'state', 'author', 'created_at')
