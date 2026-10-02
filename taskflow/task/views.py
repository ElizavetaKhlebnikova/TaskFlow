from django_filters import rest_framework as filters
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter

from project.models import Project
from user.models import Role, ProjectMember
from .filters import TaskFilter
from .serializers import TaskSerializer

from .models import Task

from rest_framework import permissions


class TaskPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in {'POST', 'GET'}:
            project_id = None
            if request.method == 'POST':
                project_id = request.data.get('project')
            if request.method == 'GET':
                project_id = request.query_params.get('project')
            if project_id:
                project_exists = Project.objects.filter(pk=project_id).exists()
                if not project_exists:
                    return True
                return ProjectMember.objects.filter(project__id=project_id,
                                                    user=request.user).exists()
            return True
        return True


class TaskView(CreateModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [TaskPermission]
    serializer_class = TaskSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        qs = Task.objects.all().order_by('-priority')
        return qs

    def filter_queryset(self, queryset):
        if self.action == 'list':
            return super().filter_queryset(queryset)
        return queryset
