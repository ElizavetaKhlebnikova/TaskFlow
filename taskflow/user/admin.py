from django.contrib import admin
from .models import ProjectMember


@admin.register(ProjectMember)
class ProjectMember(admin.ModelAdmin):
    list_display = ['id', 'user', 'project', 'role']
