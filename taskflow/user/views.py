from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_filters import rest_framework as filters

from project.models import Project
from user.filters import ProjectMemberFilter
from user.models import ProjectMember, Role
from user.serializers import ProjectMemberSerializer


class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == "POST":
            project_id = request.data.get('project')
            project_exists = Project.objects.filter(pk=project_id).exists()
            if not project_exists:
                return True
            user = request.user
            role = self.get_role_in_project(project_id, user)
            return role == Role.MANAGER
        project_id = request.query_params.get('project')
        if request.method == "GET":
            if project_id:
                project_exists = Project.objects.filter(pk=project_id).exists()
                if not project_exists:
                    return True
                return Project.objects.filter(pk=project_id, members__user=request.user).exists()
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in {"DELETE", "PATCH"}:
            project_id = obj.project.id
            return self.get_role_in_project(project_id, request.user) == Role.MANAGER

    @staticmethod
    def get_role_in_project(project_id: int, user: User):
        member = ProjectMember.objects.filter(project__id=project_id, user=user).first()
        if member:
            return member.role


class ProjectMemberView(CreateModelMixin, ListModelMixin,
                        DestroyModelMixin, GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsMember]
    serializer_class = ProjectMemberSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProjectMemberFilter

    def get_queryset(self):
        qs = ProjectMember.objects.all()
        return qs

    def filter_queryset(self, queryset):
        if self.action == 'list':
            return super().filter_queryset(queryset)
        return queryset

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
