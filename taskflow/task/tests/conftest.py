import pytest
from rest_framework.test import APIClient
from task.models import Project, Task, Status, Priority, Comment
from user.models import ProjectMember, Role

from django.contrib.auth.models import User


@pytest.fixture
def user_manager():
    return User.objects.create_user(
        username="Alise",
        password="123456"
    )


@pytest.fixture
def user_member_assignee():
    return User.objects.create_user(
        username="Assignee",
        password="123456"
    )


@pytest.fixture
def user_member_author():
    return User.objects.create_user(
        username="Author",
        password="123456"
    )


@pytest.fixture
def not_member():
    return User.objects.create_user(
        username="Not member",
        password="123456"
    )


@pytest.fixture
def project(user_manager):
    return Project.objects.create(
        name='Test project',
        description='-',
        owner=user_manager
    )


@pytest.fixture
def member_assignee(user_member_assignee, project):
    return ProjectMember.objects.create(
        user=user_member_assignee,
        project=project,
        role=Role.MEMBER
    )


@pytest.fixture
def member_author(user_member_author, project):
    return ProjectMember.objects.create(
        user=user_member_author,
        project=project,
        role=Role.MEMBER
    )


@pytest.fixture
def manager(user_manager, project):
    return ProjectMember.objects.create(
        user=user_manager,
        project=project,
        role=Role.MANAGER
    )


@pytest.fixture
def task(project, user_member_assignee, user_member_author, manager,
         member_assignee, member_author):
    return Task.objects.create(project=project,
                               name="Test task 1",
                               description="-",
                               assignee=user_member_assignee,
                               status=Status.TODO,
                               priority=Priority.MEDIUM,
                               author=user_member_author
                               )


@pytest.fixture
def task_todo_medium(project, user_member_assignee, user_member_author, manager,
                     member_assignee, member_author):
    return Task.objects.create(project=project,
                               name="Test task 2",
                               description="-",
                               assignee=user_member_assignee,
                               status=Status.TODO,
                               priority=Priority.MEDIUM,
                               author=user_member_author
                               )


@pytest.fixture
def task_todo_high(project, user_member_assignee, user_member_author, manager,
                   member_assignee, member_author):
    return Task.objects.create(project=project,
                               name="Test task 3",
                               description="-",
                               assignee=user_member_assignee,
                               status=Status.TODO,
                               priority=Priority.HIGH,
                               author=user_member_author
                               )


@pytest.fixture
def task_planed_high_author_is_assignee(project, user_member_author, manager,
                                        member_author):
    return Task.objects.create(project=project,
                               name="Test task 4",
                               description="-",
                               assignee=user_member_author,
                               status=Status.PLANNED,
                               priority=Priority.HIGH,
                               author=user_member_author
                               )


@pytest.fixture
def authenticated_client_manager(user_manager, manager):
    client = APIClient()
    client.force_authenticate(user=user_manager)
    return client


@pytest.fixture
def authenticated_client_member_assignee(user_member_assignee, member_assignee):
    client = APIClient()
    client.force_authenticate(user=user_member_assignee)
    return client


@pytest.fixture
def authenticated_client_member_author(user_member_author, member_author):
    client = APIClient()
    client.force_authenticate(user=user_member_author)
    return client


@pytest.fixture
def authenticated_client_not_member(not_member):
    client = APIClient()
    client.force_authenticate(user=not_member)
    return client


@pytest.fixture
def comment_task_by_author(task, user_member_author):
    return Comment.objects.create(
        task=task,
        author=user_member_author,
        text='Задача готова?'
    )


@pytest.fixture
def comment_task_by_assignee(task, user_member_assignee):
    return Comment.objects.create(
        task=task,
        author=user_member_assignee,
        text='нет'
    )


@pytest.fixture
def comment_task_todo_medium_by_author(task_todo_medium, user_member_author):
    return Comment.objects.create(
        task=task_todo_medium,
        author=user_member_author,
        text='Задача готова?'
    )


@pytest.fixture
def comment_task_todo_medium_by_assignee(task_todo_medium, user_member_assignee):
    return Comment.objects.create(
        task=task_todo_medium,
        author=user_member_assignee,
        text='нет'
    )


@pytest.fixture
def task_history_new_obj(
        authenticated_client_manager,
        user_member_assignee,
        user_manager,
        project,
        member_assignee,
        member_author
):
    response = authenticated_client_manager.post(
        f"/api/task/",
        {
            "project": project.pk,
            "name": "Test task 1",
            "status": Status.TODO,
            "priority": Priority.HIGH,
            "description": "Description",
            "assignee": user_member_assignee.pk,
        },
        format="json"
    )
    task = Task.objects.get(id=response.data['id'])
    return task


@pytest.fixture
def task_with_history(
        authenticated_client_member_author,
        user_member_assignee,
        user_member_author,
        project,
        member_assignee,
        member_author
):
    response = authenticated_client_member_author.post(
        f"/api/task/",
        {
            "project": project.pk,
            "name": "Test task 1",
            "status": Status.TODO,
            "priority": Priority.HIGH,
            "description": "Description",
            "assignee": user_member_assignee.pk,
        },
        format="json"
    )
    task = Task.objects.get(id=response.data['id'])
    response = authenticated_client_member_author.patch(
        f"/api/task/{task.pk}/",
        {
            "name": "Test task 2",
        },
        format="json"
    )
    assert response.status_code == 200
    task.refresh_from_db()
    return task
