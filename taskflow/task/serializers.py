from rest_framework import serializers
from task.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'project', 'name', 'description', 'assignee',
                  'status', 'priority', 'author']
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
