import django_filters

from project.models import Project
from .models import ProjectMember


class ProjectMemberFilter(django_filters.FilterSet):
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all(), required=True)

    class Meta:
        model = ProjectMember
        fields = ['project']
