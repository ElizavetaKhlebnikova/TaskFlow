import datetime
import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from .models import Project, Task, Status, Priority
from user.models import ProjectMember, Role

from django.contrib.auth.models import User


@pytest.fixture
def user_alice():
    return User.objects.create_user(
        username="Alise",
        password="123456"
    )


@pytest.fixture
def user_bob():
    return User.objects.create_user(
        username="Bob",
        password="123456"
    )


@pytest.fixture
def not_member():
    return User.objects.create_user(
        username="Not member",
        password="123456"
    )


@pytest.fixture
def authenticated_client_alice(user_alice, manager):
    client = APIClient()
    client.force_authenticate(user=user_alice)
    return client


@pytest.fixture
def authenticated_client_bob(user_bob, member):
    client = APIClient()
    client.force_authenticate(user=user_bob)
    return client


@pytest.fixture
def authenticated_client_not_member(not_member):
    client = APIClient()
    client.force_authenticate(user=not_member)
    return client


@pytest.fixture
def project(user_alice):
    return Project.objects.create(
        name='Test project',
        description='-',
        owner=user_alice
    )


@pytest.fixture
def member(user_bob, project):
    return ProjectMember.objects.create(
        user=user_bob,
        project=project,
        role=Role.MEMBER
    )


@pytest.fixture
def manager(user_alice, project):
    return ProjectMember.objects.create(
        user=user_alice,
        project=project,
        role=Role.MANAGER
    )


@pytest.mark.django_db
def test_create_task_unauthorised():
    client = APIClient()

    response = client.post(
        "/api/task/",
        {
            "project": 1,
            "title": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": 5,
            "status": "todo",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_create_task_by_not_member(authenticated_client_not_member, project, user_alice):
    response = authenticated_client_not_member.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_alice.pk,
            "status": "todo",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_task_by_manager(authenticated_client_alice, project, user_bob, user_alice):
    response = authenticated_client_alice.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_bob.pk,
            "status": "todo",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 201
    task_id = response.data['id']
    task = Task.objects.get(id=task_id)
    assert task.project == project
    assert task.assignee == user_bob
    assert task.author == user_alice
    assert task.status == Status.TODO
    assert task.priority == Priority.HIGH


@pytest.mark.django_db
def test_create_task_by_member(authenticated_client_bob, project, user_bob, user_alice):
    response = authenticated_client_bob.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_alice.pk,
            "status": "todo",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 201
    task_id = response.data['id']
    task = Task.objects.get(id=task_id)
    assert task.project == project
    assert task.assignee == user_alice
    assert task.author == user_bob
    assert task.status == Status.TODO
    assert task.priority == Priority.HIGH


@pytest.mark.django_db
def test_create_task_invalid_project(authenticated_client_alice, user_bob):
    response = authenticated_client_alice.post(
        "/api/task/",
        {
            "project": 9999,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_bob.pk,
            "status": "todo",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_task_without_project(authenticated_client_alice, user_bob):
    response = authenticated_client_alice.post(
        "/api/task/",
        {
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_bob.pk,
            "status": "todo",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_task_invalid_assignee(authenticated_client_alice, project):
    response = authenticated_client_alice.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": 9999,
            "status": "todo",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_task_invalid_status(authenticated_client_alice, project, user_bob):
    response = authenticated_client_alice.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_bob.pk,
            "status": "invalid",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_task_invalid_priority(authenticated_client_alice, project, user_bob):
    response = authenticated_client_alice.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_bob.pk,
            "status": "todo",
            "priority": "invalid"
        },
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_list_task_unauthorised(project):
    client = APIClient()

    response = client.get(
        f"/api/task/?project={project.pk}",
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_task_by_not_member(authenticated_client_not_member, project, user_alice):
    response = authenticated_client_not_member.get(
        f"/api/task/?project={project.pk}",
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_list_task_by_manager(authenticated_client_alice, project, user_bob, user_alice):
    Task.objects.create(project=project,
                        name="Test task 1",
                        description="-",
                        assignee=user_bob,
                        status=Status.TODO,
                        priority=Priority.HIGH,
                        author=user_alice
                        )
    Task.objects.create(project=project,
                        name="Test task 2",
                        description="-",
                        assignee=user_bob,
                        status=Status.TODO,
                        priority=Priority.HIGH,
                        author=user_alice
                        )
    Task.objects.create(project=project,
                        name="Test task 3",
                        description="-",
                        assignee=user_bob,
                        status=Status.PLANNED,
                        priority=Priority.HIGH,
                        author=user_alice
                        )

    response = authenticated_client_alice.get(
        f"/api/task/?project={project.pk}",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 3


@pytest.mark.django_db
def test_list_task_by_member(authenticated_client_bob, project, user_bob, user_alice):
    Task.objects.create(project=project,
                        name="Test task 1",
                        description="-",
                        assignee=user_bob,
                        status=Status.TODO,
                        priority=Priority.HIGH,
                        author=user_alice
                        )
    Task.objects.create(project=project,
                        name="Test task 2",
                        description="-",
                        assignee=user_bob,
                        status=Status.TODO,
                        priority=Priority.HIGH,
                        author=user_alice
                        )
    Task.objects.create(project=project,
                        name="Test task 3",
                        description="-",
                        assignee=user_bob,
                        status=Status.PLANNED,
                        priority=Priority.HIGH,
                        author=user_alice
                        )

    response = authenticated_client_bob.get(
        f"/api/task/?project={project.pk}",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 3


@pytest.mark.django_db
def test_list_task_without_project(authenticated_client_bob):
    response = authenticated_client_bob.get(
        f"/api/task/",
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_list_task_with_status_filter(authenticated_client_alice, project, user_bob, user_alice):
    task_1 = Task.objects.create(project=project,
                                 name="Test task 1",
                                 description="-",
                                 assignee=user_bob,
                                 status=Status.TODO,
                                 priority=Priority.HIGH,
                                 author=user_alice
                                 )
    task_2 = Task.objects.create(project=project,
                                 name="Test task 2",
                                 description="-",
                                 assignee=user_bob,
                                 status=Status.TODO,
                                 priority=Priority.HIGH,
                                 author=user_alice
                                 )
    task_3 = Task.objects.create(project=project,
                                 name="Test task 3",
                                 description="-",
                                 assignee=user_bob,
                                 status=Status.PLANNED,
                                 priority=Priority.HIGH,
                                 author=user_alice
                                 )

    response = authenticated_client_alice.get(
        f"/api/task/?project={project.pk}&status=todo",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {task_1.pk, task_2.pk}


@pytest.mark.django_db
def test_list_task_with_priority_filter(authenticated_client_alice, project, user_bob, user_alice):
    task_1 = Task.objects.create(project=project,
                                 name="Test task 1",
                                 description="-",
                                 assignee=user_bob,
                                 status=Status.TODO,
                                 priority=Priority.MEDIUM,
                                 author=user_alice
                                 )
    task_2 = Task.objects.create(project=project,
                                 name="Test task 2",
                                 description="-",
                                 assignee=user_bob,
                                 status=Status.TODO,
                                 priority=Priority.HIGH,
                                 author=user_alice
                                 )
    task_3 = Task.objects.create(project=project,
                                 name="Test task 3",
                                 description="-",
                                 assignee=user_bob,
                                 status=Status.PLANNED,
                                 priority=Priority.HIGH,
                                 author=user_alice
                                 )

    response = authenticated_client_alice.get(
        f"/api/task/?project={project.pk}&priority=high",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {task_2.pk, task_3.pk}


@pytest.mark.django_db
def test_list_task_with_assignee_filter(authenticated_client_alice, project, user_bob, user_alice):
    task_1 = Task.objects.create(project=project,
                                 name="Test task 1",
                                 description="-",
                                 assignee=user_bob,
                                 status=Status.TODO,
                                 priority=Priority.MEDIUM,
                                 author=user_alice
                                 )
    task_2 = Task.objects.create(project=project,
                                 name="Test task 2",
                                 description="-",
                                 assignee=user_alice,
                                 status=Status.TODO,
                                 priority=Priority.HIGH,
                                 author=user_alice
                                 )
    task_3 = Task.objects.create(project=project,
                                 name="Test task 3",
                                 description="-",
                                 assignee=user_bob,
                                 status=Status.PLANNED,
                                 priority=Priority.HIGH,
                                 author=user_alice
                                 )

    response = authenticated_client_alice.get(
        f"/api/task/?project={project.pk}&assignee={user_bob.pk}",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {task_1.pk, task_3.pk}


@pytest.mark.django_db
def test_list_task_invalid_project(authenticated_client_not_member):
    response = authenticated_client_not_member.get(
        f"/api/task/?project=9999",
        format="json"
    )

    assert response.status_code == 400
