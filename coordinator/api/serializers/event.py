from rest_framework import serializers
from coordinator.api.models import Event


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
