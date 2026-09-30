from django_filters import rest_framework as filters
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from .filters import ProjectFilter
from .serializers import ProjectSerializer

from .models import Project


class ProjectPagination(PageNumberPagination):
    page_size = 10


class ProjectView(CreateModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    pagination_class = ProjectPagination
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ProjectFilter
    search_fields = ['name']
    ordering_fields = ['updated_at', 'name']

    def get_queryset(self):
        return Project.objects.filter(members__user=self.request.user).order_by('-updated_at')
