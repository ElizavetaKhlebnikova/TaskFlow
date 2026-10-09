import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from reversion.models import Version

from task.models import Task, Status, Priority


@pytest.mark.django_db
def test_delete_task_unauthorised(task):
    client = APIClient()

    response = client.delete(
        f"/api/task/{task.pk}/",
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_delete_task_by_manager(task, authenticated_client_manager):
    response = authenticated_client_manager.delete(
        f"/api/task/{task.pk}/",
        format="json"
    )

    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_task_by_author(task, authenticated_client_member_author):
    response = authenticated_client_member_author.delete(
        f"/api/task/{task.pk}/",
        format="json"
    )

    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_task_by_assignee(task, authenticated_client_member_assignee):
    response = authenticated_client_member_assignee.delete(
        f"/api/task/{task.pk}/",
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_task_by_not_member(task, authenticated_client_not_member):
    response = authenticated_client_not_member.delete(
        f"/api/task/{task.pk}/",
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_task_by_not_member_but_author(task, authenticated_client_not_member, not_member):
    task.author = not_member
    task.save()
    response = authenticated_client_not_member.delete(
        f"/api/task/{task.pk}/",
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_task_by_not_member_but_assignee(task, authenticated_client_not_member, not_member):
    task.assignee = not_member
    task.save()
    response = authenticated_client_not_member.delete(
        f"/api/task/{task.pk}/",
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_task_invalid_task(authenticated_client_manager):
    response = authenticated_client_manager.delete(
        f"/api/task/9999/",
        format="json"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_task_versions(
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

    task_id = task.id
    response = authenticated_client_manager.delete(
        f"/api/task/{task_id}/",
        format="json"
    )

    assert response.status_code == 204
    versions = Version.objects.get_deleted(Task)
    version = versions.get(object_id=str(task_id))
    assert version.revision.user == user_manager
    assert version.field_dict['name'] == "Test task 1"

    version.revert()
    task = Task.objects.get(id=task_id)
    assert task.name == "Test task 1"
