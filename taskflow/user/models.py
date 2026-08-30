from django.db import models

from django.contrib.auth.models import User
from project.models import Project


class Role(models.TextChoices):
    MANAGER = "manager", "Manager"
    MEMBER = "member", "Member"


class ProjectMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    project = models.ForeignKey(Project, related_name='members', verbose_name='Проект', on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.MEMBER
    )

    class Meta:
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'участники проектов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'project'],
                name='unique_user_project'
            )
        ]

