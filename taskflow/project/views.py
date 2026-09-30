from django_filters import rest_framework as filters
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter

from user.models import Role
from .filters import ProjectFilter
from .serializers import ProjectSerializer

from .models import Project

from rest_framework import permissions


class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user == obj.owner
        elif request.method in ('PATCH', 'PUT'):
            return obj.members.filter(role=Role.MANAGER, user=request.user).exists()
        else:
            return obj.members.filter(user=request.user).exists()


class ProjectPagination(PageNumberPagination):
    page_size = 10


class ProjectView(CreateModelMixin, ListModelMixin, RetrieveModelMixin,
                  UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsManagerOrReadOnly]
    serializer_class = ProjectSerializer
    pagination_class = ProjectPagination
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ProjectFilter
    search_fields = ['name']
    ordering_fields = ['updated_at', 'name']

    def get_queryset(self):
        qs = Project.objects.all().order_by('-updated_at')
        if self.action == 'list':
            return qs.filter(members__user=self.request.user)
        return qs
