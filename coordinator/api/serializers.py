from coordinator.api.models import Task, TaskService, Release
from rest_framework import serializers


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ('kf_id', 'state', 'progress', 'created_at')
        read_only_fields = ('kf_id', 'state', 'created_at')


class TaskServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaskService
        fields = ('kf_id', 'name', 'health_status', 'url', 'created_at')
        read_only_fields = ('kf_id', 'health_status', 'created_at')


class ReleaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Release
        fields = ('kf_id', 'name', 'state', 'studies', 'created_at')
        read_only_fields = ('kf_id', 'name', 'state', 'created_at')
