from django.db import models
from django.contrib.auth.models import User

from project.models import Project


class Status(models.TextChoices):
    PLANNED = "planned", "Planned"
    TODO = "todo", "ToDo"
    IN_PROGRESS = "in_progress", "In progress"
    DONE = "done", "Done"


class Priority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


class Task(models.Model):
    name = models.CharField('Название', max_length=256)
    description = models.TextField('Описание', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name='Проект')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='authored_tasks',
                               verbose_name='Автор', null=True, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_tasks',
                                 verbose_name='Исполнитель', null=True, blank=True)
    status = models.CharField(
        'Статус', max_length=20, choices=Status.choices, default=Status.PLANNED
    )
    priority = models.CharField(
        'Приоритет', max_length=20, choices=Priority.choices, null=True, blank=True
    )
    deadline = models.DateTimeField('Дедлайн', null=True, blank=True)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'задачи'

    def __str__(self):
        return f'{self.project}: {self.name}'


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name='Задача')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='comments', verbose_name='Автор',
                               null=True, blank=True)
    text = models.TextField('Текст')

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'комментарии'
