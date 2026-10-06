import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


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
