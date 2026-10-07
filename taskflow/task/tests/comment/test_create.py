import pytest
from rest_framework.test import APIClient
from task.models import Comment


@pytest.mark.django_db
def test_create_comment_unauthorised(task):
    client = APIClient()

    response = client.post(
        "/api/comments/",
        {
            "task": task.pk,
            "text": "Проверил задачу, всё готово."
        },
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_create_comment_by_not_member(authenticated_client_not_member, task):
    response = authenticated_client_not_member.post(
        "/api/comments/",
        {
            "task": task.pk,
            "text": "Проверил задачу, всё готово."
        },
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_comment_by_manager(authenticated_client_manager, task, user_manager):
    response = authenticated_client_manager.post(
        "/api/comments/",
        {
            "task": task.pk,
            "text": "Проверил задачу, всё готово."
        },
        format="json"
    )
    assert response.status_code == 201
    comment_id = response.data['id']
    comment = Comment.objects.get(id=comment_id)
    assert comment.task == task
    assert comment.author == user_manager


@pytest.mark.django_db
def test_create_comment_by_manager_make_author(authenticated_client_manager, task, user_manager, user_member_assignee):
    response = authenticated_client_manager.post(
        "/api/comments/",
        {
            "task": task.pk,
            "text": "Проверил задачу, всё готово.",
            "author": user_member_assignee.pk
        },
        format="json"
    )
    assert response.status_code == 201
    comment_id = response.data['id']
    comment = Comment.objects.get(id=comment_id)
    assert comment.task == task
    assert comment.author == user_manager


@pytest.mark.django_db
def test_create_comment_invalid_task(authenticated_client_manager):
    response = authenticated_client_manager.post(
        "/api/comments/",
        {
            "task": 9999,
            "text": "Проверил задачу, всё готово.",
        },
        format="json"
    )
    assert response.status_code == 400
