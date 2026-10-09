from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import Task, Comment


@admin.register(Task)
class TaskAdmin(VersionAdmin):
    list_display = ['id', 'name', 'project', 'author', 'assignee', 'status', 'priority', 'deadline']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'author']

