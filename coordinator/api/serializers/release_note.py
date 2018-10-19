from rest_framework import serializers
from coordinator.api.models import ReleaseNote


class ReleaseNoteSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ReleaseNote
        fields = ('kf_id', 'description', 'author', 'created_at', 'release',
                  'study')
        read_only_fields = ('kf_id', 'created_at')
        extra_kwargs = {
            'release': {'allow_null': True, 'lookup_field': 'kf_id'},
            'study': {'view_name': 'studies-detail',
                      'allow_null': True,
                      'lookup_field': 'kf_id'},
        }
