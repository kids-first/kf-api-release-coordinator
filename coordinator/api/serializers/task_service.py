from rest_framework import serializers
from coordinator.api.models import TaskService


class TaskServiceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TaskService
        fields = ('kf_id', 'name', 'description', 'last_ok_status', 'author',
                  'health_status', 'url', 'created_at', 'enabled')
        read_only_fields = ('kf_id', 'last_ok_status', 'health_status',
                            'created_at')
