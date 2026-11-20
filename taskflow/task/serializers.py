from rest_framework import serializers
from reversion.models import Version

from task.models import Task, Comment
from user.models import ProjectMember


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'project', 'name', 'description', 'assignee', 'status',
                  'priority', 'deadline', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance is not None:
            self.fields['project'].read_only = True

    def create(self, validated_data):
        request = self.context["request"]
        task = super().create(validated_data)
        task.author = request.user
        task.save(update_fields=['author'])
        return task

    def validate_assignee(self, value):
        """
        Check that the assignee is project member.
        """
        if self.instance:
            project = self.instance.project
            if not ProjectMember.objects.filter(project=project, user=value).exists():
                raise serializers.ValidationError("Исполнитель должен быть участником проекта")
        else:
            project_id = self.initial_data.get('project')
            if project_id:
                if not ProjectMember.objects.filter(project__id=project_id, user=value).exists():
                    raise serializers.ValidationError("Исполнитель должен быть участником проекта")
        return value


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance is not None:
            self.fields['task'].read_only = True

    def create(self, validated_data):
        request = self.context['request']
        comment = super().create(validated_data)
        comment.author = request.user
        comment.save(update_fields=['author'])
        return comment


class TaskHistorySerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='revision.user.pk')
    date_created = serializers.DateTimeField(source='revision.date_created')

    class Meta:
        model = Version
        fields = ['id', 'revision', 'user', 'date_created', 'field_dict']
        read_only_fields = ['id', 'revision', 'user', 'date_created', 'field_dict']
