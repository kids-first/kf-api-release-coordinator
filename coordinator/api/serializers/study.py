from rest_framework import serializers
from coordinator.api.models import Study


class StudySerializer(serializers.HyperlinkedModelSerializer):

    version = serializers.CharField(source='latest_version', allow_blank=True)

    class Meta:
        model = Study
        fields = ('kf_id', 'name', 'version', 'visible',
                  'deleted', 'created_at')
