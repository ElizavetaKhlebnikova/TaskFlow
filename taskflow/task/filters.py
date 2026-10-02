import django_filters
from django.contrib.auth.models import User

from project.models import Project
from .models import Task

PRIORITY_FILTER_CHOICES = (
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High")
)

STATUS_FILTER_CHOICES = (
    ("planned", "Planned"),
    ("todo", "ToDo"),
    ("in_progress", "In progress"),
    ("done", "Done")
)


class TaskFilter(django_filters.FilterSet):
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all(), required=True)
    priority = django_filters.ChoiceFilter(choices=PRIORITY_FILTER_CHOICES)
    status = django_filters.ChoiceFilter(choices=STATUS_FILTER_CHOICES)
    assignee = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Task
        fields = ['project', 'priority', 'status', 'assignee']
