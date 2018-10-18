from rest_framework import serializers
from coordinator.api.models import Task


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
