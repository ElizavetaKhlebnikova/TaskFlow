from rest_framework import routers

from project.views import ProjectView
from user.views import ProjectMemberView
from task.views import TaskView

router = routers.DefaultRouter()

router.register('projects', ProjectView, basename='projects')
router.register('project-members', ProjectMemberView, basename='project_members')
router.register('task', TaskView, basename='task')

urlpatterns = router.urls
