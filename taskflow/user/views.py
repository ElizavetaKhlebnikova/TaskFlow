from rest_framework import permissions
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_filters import rest_framework as filters

from project.models import Project
from user.filters import ProjectMemberFilter
from user.models import ProjectMember
from user.serializers import ProjectMemberSerializer


class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        project_id = request.query_params.get('project')

        if project_id:
            project_exists = Project.objects.filter(pk=project_id).exists()
            if not project_exists:
                return True
            return Project.objects.filter(pk=project_id, members__user=request.user).exists()
        return True


class ProjectMemberView(ListModelMixin, GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsMember]
    serializer_class = ProjectMemberSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProjectMemberFilter

    def get_queryset(self):
        qs = ProjectMember.objects.all()
        return qs

