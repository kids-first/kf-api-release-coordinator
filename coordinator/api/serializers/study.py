from rest_framework import serializers
from coordinator.api.models import Study


class StudySerializer(serializers.HyperlinkedModelSerializer):

    version = serializers.CharField(source='latest_version', allow_blank=True)

    last_pub_version = serializers.CharField(source='last_published_version',
                                             allow_blank=True)
    last_pub_date = serializers.DateTimeField(source='last_published_date')

    class Meta:
        model = Study
        fields = ('kf_id', 'name', 'version', 'visible', 'last_pub_version',
                  'last_pub_date', 'deleted', 'created_at')
