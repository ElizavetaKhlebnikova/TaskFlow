import datetime

import pytest
from rest_framework.test import APIClient
from task.models import Task, Status, Priority
from user.models import ProjectMember


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
def test_create_task_by_not_member(authenticated_client_not_member, project, user_manager):
    response = authenticated_client_not_member.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_manager.pk,
            "status": "todo",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_task_by_manager(authenticated_client_manager, project, member_assignee, user_manager):
    deadline = datetime.datetime(year=2026, month=10, day=20, hour=18, tzinfo=datetime.timezone.utc)
    deadline_string = deadline.strftime('%Y-%m-%dT%H:%M:%SZ')
    response = authenticated_client_manager.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": member_assignee.user.pk,
            "status": "todo",
            "priority": "high",
            "deadline": deadline_string
        },
        format="json"
    )
    assert response.status_code == 201
    task_id = response.data['id']
    task = Task.objects.get(id=task_id)
    assert task.project == project
    assert task.assignee == member_assignee.user
    assert task.author == user_manager
    assert task.status == Status.TODO
    assert task.priority == Priority.HIGH
    assert task.deadline == deadline


@pytest.mark.django_db
def test_create_task_by_member(authenticated_client_member_author, project, member_author, member_assignee):
    deadline = datetime.datetime(year=2026, month=10, day=20, hour=18, tzinfo=datetime.timezone.utc)
    deadline_string = deadline.strftime('%Y-%m-%dT%H:%M:%SZ')
    response = authenticated_client_member_author.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": member_assignee.user.pk,
            "status": "todo",
            "priority": "high",
            "deadline": deadline_string
        },
        format="json"
    )

    assert response.status_code == 201
    task_id = response.data['id']
    task = Task.objects.get(id=task_id)
    assert task.project == project
    assert task.assignee == member_assignee.user
    assert task.author == member_author.user
    assert task.status == Status.TODO
    assert task.priority == Priority.HIGH
    assert task.deadline == deadline


@pytest.mark.django_db
def test_create_task_invalid_project(authenticated_client_member_author, user_member_assignee):
    response = authenticated_client_member_author.post(
        "/api/task/",
        {
            "project": 9999,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_member_assignee.pk,
            "status": "todo",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_task_without_project(authenticated_client_member_author, user_member_assignee):
    response = authenticated_client_member_author.post(
        "/api/task/",
        {
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_member_assignee.pk,
            "status": "todo",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_task_invalid_assignee(authenticated_client_member_author, project):
    response = authenticated_client_member_author.post(
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
def test_create_task_invalid_status(authenticated_client_member_author, project, user_member_assignee):
    response = authenticated_client_member_author.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_member_assignee.pk,
            "status": "invalid",
            "priority": "high"
        },
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_task_invalid_priority(authenticated_client_member_author, project, user_member_assignee):
    response = authenticated_client_member_author.post(
        "/api/task/",
        {
            "project": project.pk,
            "name": "Implement authentication",
            "description": "Add JWT authentication",
            "assignee": user_member_assignee.pk,
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
def test_list_task_by_not_member(authenticated_client_not_member, project):
    response = authenticated_client_not_member.get(
        f"/api/task/?project={project.pk}",
        format="json"
    )

    assert response.status_code == 403
