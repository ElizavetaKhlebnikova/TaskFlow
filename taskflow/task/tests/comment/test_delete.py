import pytest
from rest_framework.test import APIClient
from django.db import connection
from django.test.utils import CaptureQueriesContext


@pytest.mark.django_db
def test_delete_comment_unauthorised(comment_task_by_author):
    client = APIClient()
    response = client.delete(
        f"/api/comments/{comment_task_by_author.pk}/",
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_delete_comment_by_author(comment_task_by_author, authenticated_client_member_author):
    with CaptureQueriesContext(connection) as queries:
        response = authenticated_client_member_author.delete(
            f"/api/comments/{comment_task_by_author.pk}/",
            format="json"
        )

    print(f"Количество запросов: {len(queries)}")

    for query in queries:
        print(query["sql"])

    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_comment_by_manager(comment_task_by_author, authenticated_client_manager):
    response = authenticated_client_manager.delete(
        f"/api/comments/{comment_task_by_author.pk}/",
        format="json"
    )

    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_comment_by_another_member(comment_task_by_author, authenticated_client_member_assignee):
    response = authenticated_client_member_assignee.delete(
        f"/api/comments/{comment_task_by_author.pk}/",
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_comment_by_not_member(comment_task_by_author, authenticated_client_not_member):
    response = authenticated_client_not_member.delete(
        f"/api/comments/{comment_task_by_author.pk}/",
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_comment_by_not_member_but_author(comment_task_by_author,
                                                 authenticated_client_not_member,
                                                 not_member):
    comment_task_by_author.author = not_member
    comment_task_by_author.save()

    response = authenticated_client_not_member.delete(
        f"/api/comments/{comment_task_by_author.pk}/",
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_comment_invalid_comment(authenticated_client_manager):
    response = authenticated_client_manager.delete(
        f"/api/comments/9999/",
        format="json"
    )

    assert response.status_code == 404
