import datetime

import pytest
from rest_framework.test import APIClient
from reversion.models import Version

from task.models import Project, Status, Priority, Task


@pytest.mark.django_db
def test_partial_update_task_unauthorised(task):
    client = APIClient()
    response = client.patch(
        f"/api/task/{task.pk}/",
        {
            "name": "Implement authentication",
        },
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_partial_update_task_by_manager(task, authenticated_client_manager, user_member_assignee):
    deadline = datetime.datetime(year=2026, month=10, day=20, hour=18, tzinfo=datetime.timezone.utc)
    deadline_string = deadline.strftime('%Y-%m-%dT%H:%M:%SZ')
    new_name = "Test task 2"
    response = authenticated_client_manager.patch(
        f"/api/task/{task.pk}/",
        {
            "name": new_name,
            "status": Status.DONE,
            "priority": Priority.HIGH,
            "description": "new description",
            "assignee": user_member_assignee.pk,
            "deadline": deadline_string
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data['name'] == new_name
    task.refresh_from_db()
    assert task.name == new_name
    assert task.status == Status.DONE
    assert task.priority == Priority.HIGH
    assert task.description == "new description"
    assert task.assignee == user_member_assignee
    assert task.deadline == deadline


@pytest.mark.django_db
def test_partial_update_task_by_author(task, authenticated_client_member_author):
    new_name = "Test task 2"

    response = authenticated_client_member_author.patch(
        f"/api/task/{task.pk}/",
        {
            "name": new_name,
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data['name'] == new_name
    task.refresh_from_db()
    assert task.name == new_name


@pytest.mark.django_db
def test_partial_update_task_by_assignee(task, authenticated_client_member_assignee):
    new_name = "Test task 2"

    response = authenticated_client_member_assignee.patch(
        f"/api/task/{task.pk}/",
        {
            "name": new_name,
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data['name'] == new_name
    task.refresh_from_db()
    assert task.name == new_name


@pytest.mark.django_db
def test_partial_update_task_by_not_member(authenticated_client_not_member, task):
    new_name = "Test task 2"

    response = authenticated_client_not_member.patch(
        f"/api/task/{task.pk}/",
        {
            "name": new_name,
        },
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_partial_update_task_invalid_task(authenticated_client_manager):
    new_name = "Test task 2"
    response = authenticated_client_manager.patch(
        f"/api/task/9999/",
        {
            "name": new_name,
        },
        format="json"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_partial_update_task_change_project(project, authenticated_client_member_author, user_manager, task):
    new_project = Project.objects.create(
        name='Test project second',
        description='-',
        owner=user_manager
    )

    response = authenticated_client_member_author.patch(
        f"/api/task/{task.pk}/",
        {
            "project": new_project.pk,
        },
        format="json"
    )

    assert response.status_code == 200
    task.refresh_from_db()
    assert task.project == project


@pytest.mark.django_db
def test_partial_update_task_change_author(task, authenticated_client_member_author, user_manager, user_member_author):
    response = authenticated_client_member_author.patch(
        f"/api/task/{task.pk}/",
        {
            "author": user_manager.pk,
        },
        format="json"
    )

    assert response.status_code == 200
    task.refresh_from_db()
    assert task.author == user_member_author


@pytest.mark.django_db
def test_partial_update_task_by_not_member_but_author(task, authenticated_client_not_member, not_member):
    task.author = not_member
    task.save()
    new_name = "Test task 2"
    response = authenticated_client_not_member.patch(
        f"/api/task/{task.pk}/",
        {
            "name": new_name,
        },
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_partial_update_task_by_not_member_but_assignee(task, authenticated_client_not_member, not_member):
    task.assignee = not_member
    task.save()
    new_name = "Test task 2"
    response = authenticated_client_not_member.patch(
        f"/api/task/{task.pk}/",
        {
            "name": new_name,
        },
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_partial_update_task_assignee_is_not_member(task, authenticated_client_manager, not_member):
    response = authenticated_client_manager.patch(
        f"/api/task/{task.pk}/",
        {
            "assignee": not_member.pk,
        },
        format="json"
    )

    assert response.status_code == 400
    assert response.data['assignee'][0] == "Исполнитель должен быть участником проекта"


@pytest.mark.django_db
def test_partial_update_task_versions(
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

    assert response.status_code == 201
    task = Task.objects.get(id=response.data['id'])
    versions = Version.objects.get_for_object(task)
    assert len(versions) == 1
    assert versions[0].revision.user == user_manager
    assert versions[0].field_dict['name'] == "Test task 1"

    response = authenticated_client_manager.patch(
        f"/api/task/{task.pk}/",
        {
            "name": "Test task 2",
        },
        format="json"
    )
    assert response.status_code == 200
    task.refresh_from_db()
    assert task.name == "Test task 2"

    versions = Version.objects.get_for_object(task)
    assert len(versions) == 2
    assert versions[0].revision.user == user_manager

    assert versions[0].field_dict['name'] == "Test task 2"
    assert versions[1].field_dict['name'] == "Test task 1"

    versions[1].revision.revert()
    task.refresh_from_db()
    assert task.name == "Test task 1"
