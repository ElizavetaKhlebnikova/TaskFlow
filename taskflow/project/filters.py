import django_filters
from .models import Project


ROLE_FILTER_CHOICES = (
    ('member', 'Member'),
    ('manager', 'Manager'),
)


class ProjectFilter(django_filters.FilterSet):
    role = django_filters.ChoiceFilter(method='filter_role', choices=ROLE_FILTER_CHOICES)

    class Meta:
        model = Project
        fields = ['role']

    def filter_role(self, queryset, name, value):
        if value:
            return queryset.filter(members__role=value, members__user=self.request.user)
        else:
            return queryset
