from rest_framework import serializers
from user.models import ProjectMember


class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'project', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance is not None:
            self.fields['user'].read_only = True
            self.fields['project'].read_only = True



