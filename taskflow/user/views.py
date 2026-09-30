from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

from project.models import Project


class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        project_id = request.query_params.get('project')
        if request.user.is_authenticated:
            if project_id:
                return Project.objects.filter(pk=project_id, members__user=request.user).exists()
        return False


class ProjectMemberView(ListModelMixin, GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsMember]

