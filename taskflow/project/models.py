from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Project(models.Model):
    name = models.CharField('Название', max_length=256)
    description = models.TextField('Описание', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='owned_projects', verbose_name='Автор',
                              null=True, blank=True)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'проекты'

    def __str__(self):
        return self.name
