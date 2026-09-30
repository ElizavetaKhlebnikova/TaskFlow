from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project
from user.models import ProjectMember, Role


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context["request"]
        with transaction.atomic():
            project = super().create(validated_data)
            project.owner = request.user
            project.save(update_fields=["owner"])
            ProjectMember.objects.create(user=request.user,
                                         project=project,
                                         role=Role.MANAGER)
            return project
