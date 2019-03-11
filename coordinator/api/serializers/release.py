from rest_framework import serializers
from coordinator.api.models import Release, Study
from .task import TaskSerializer
from .release_note import ReleaseNoteSerializer


class ReleaseSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.ListField(
                child=serializers.CharField(max_length=50,
                                            allow_blank=False,
                                            validators=[]),
                allow_empty=True,
                required=False)

    studies = serializers.PrimaryKeyRelatedField(queryset=Study.objects.all(),
                                                 many=True)

    def validate_studies(self, studies):
        if len(studies) == 0:
            raise serializers.ValidationError('Must have at least one study')
        return studies

    tasks = TaskSerializer(read_only=True, many=True)
    notes = ReleaseNoteSerializer(read_only=True, many=True)

    class Meta:
        model = Release
        fields = ('kf_id', 'name', 'description', 'notes', 'state', 'studies',
                  'tasks', 'version', 'created_at', 'tags', 'author',
                  'is_major')
        read_only_fields = ('kf_id', 'state', 'tasks', 'version', 'created_at',
                            'version', 'notes')
