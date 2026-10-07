import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_partial_update_comment_by_unauthorised(comment_task_by_author):
    client = APIClient()
    new_text = "Изменённый комментарий"

    response = client.patch(
        f"/api/comments/{comment_task_by_author.pk}/",
        {
            "text": new_text
        },
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_partial_update_comment_by_member_not_author(comment_task_by_author,
                                                     authenticated_client_member_assignee):
    new_text = "Изменённый комментарий"
    response = authenticated_client_member_assignee.patch(
        f"/api/comments/{comment_task_by_author.pk}/",
        {
            "text": new_text
        },
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_partial_update_comment_by_not_member(comment_task_by_author, authenticated_client_not_member):
    new_text = "Изменённый комментарий"

    response = authenticated_client_not_member.patch(
        f"/api/comments/{comment_task_by_author.pk}/",
        {
            "text": new_text
        },
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_partial_update_comment_by_not_member_but_author(comment_task_by_author,
                                                         authenticated_client_not_member,
                                                         not_member):
    comment_task_by_author.author = not_member
    comment_task_by_author.save()

    new_text = "Изменённый комментарий"

    response = authenticated_client_not_member.patch(
        f"/api/comments/{comment_task_by_author.pk}/",
        {
            "text": new_text
        },
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_partial_update_comment_by_author(comment_task_by_author, authenticated_client_member_author):
    new_text = "Изменённый комментарий"

    response = authenticated_client_member_author.patch(
        f"/api/comments/{comment_task_by_author.pk}/",
        {
            "text": new_text
        },
        format="json"
    )

    assert response.status_code == 200
    comment_task_by_author.refresh_from_db()
    assert comment_task_by_author.text == new_text


@pytest.mark.django_db
def test_partial_update_comment_by_author_change_author(comment_task_by_author,
                                                        authenticated_client_member_author,
                                                        user_member_assignee,
                                                        user_member_author):
    response = authenticated_client_member_author.patch(
        f"/api/comments/{comment_task_by_author.pk}/",
        {
            "author": user_member_assignee.pk
        },
        format="json"
    )

    assert response.status_code == 200
    comment_task_by_author.refresh_from_db()
    assert comment_task_by_author.author == user_member_author


@pytest.mark.django_db
def test_partial_update_comment_by_author_change_task(comment_task_by_author,
                                                      authenticated_client_member_author,
                                                      task_todo_medium,
                                                      task):
    response = authenticated_client_member_author.patch(
        f"/api/comments/{comment_task_by_author.pk}/",
        {
            "task": task_todo_medium.pk
        },
        format="json"
    )

    assert response.status_code == 200
    comment_task_by_author.refresh_from_db()
    assert comment_task_by_author.task == task


@pytest.mark.django_db
def test_partial_update_comment_by_author_invalid_comment(authenticated_client_member_author):
    new_text = "Изменённый комментарий"
    response = authenticated_client_member_author.patch(
        f"/api/comments/9999/",
        {
            "text": new_text
        },
        format="json"
    )

    assert response.status_code == 404
