from django_filters import rest_framework as filters
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
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
            project_id = (
                request.data.get('project')
                if request.method == "POST"
                else request.query_params.get('project')
            )
            if project_id:
                project_exists = Project.objects.filter(pk=project_id).exists()
                if not project_exists:
                    return True
                return ProjectMember.objects.filter(project__id=project_id,
                                                    user=request.user).exists()
        return True

    def has_object_permission(self, request, view, obj: Task):
        member_role = ProjectMember.objects.filter(
            project__id=obj.project.id,
            user=request.user
        ).values_list('role', flat=True).first()
        if member_role is None:
            return False

        is_manager = member_role == Role.MANAGER
        is_author_or_assignee = request.user.pk in {
            obj.author.pk,
            obj.assignee.pk
        }
        if request.method == "PATCH":
            return is_manager or is_author_or_assignee
        if request.method == "DELETE":
            return is_manager or request.user.pk == obj.author.pk
        return True


class TaskView(CreateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet):
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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
