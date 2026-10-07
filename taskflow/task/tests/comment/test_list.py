import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_list_comment_unauthorised(comment_task_by_author,
                                   comment_task_by_assignee,
                                   comment_task_todo_medium_by_author,
                                   comment_task_todo_medium_by_assignee,
                                   task):
    client = APIClient()
    response = client.get(
        f"/api/comments/?task={task.pk}",
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_task_by_manager(authenticated_client_manager,
                              comment_task_by_author,
                              comment_task_by_assignee,
                              comment_task_todo_medium_by_author,
                              comment_task_todo_medium_by_assignee,
                              task):
    response = authenticated_client_manager.get(
        f"/api/comments/?task={task.pk}",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {comment_task_by_author.pk, comment_task_by_assignee.pk}


@pytest.mark.django_db
def test_list_task_by_member_assignee(authenticated_client_member_assignee,
                                      comment_task_by_author,
                                      comment_task_by_assignee,
                                      comment_task_todo_medium_by_author,
                                      comment_task_todo_medium_by_assignee,
                                      task_todo_medium):
    response = authenticated_client_member_assignee.get(
        f"/api/comments/?task={task_todo_medium.pk}",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {comment_task_todo_medium_by_author.pk, comment_task_todo_medium_by_assignee.pk}


@pytest.mark.django_db
def test_list_task_by_member_author(authenticated_client_member_author,
                                    comment_task_by_author,
                                    comment_task_by_assignee,
                                    comment_task_todo_medium_by_author,
                                    comment_task_todo_medium_by_assignee,
                                    task_todo_medium):
    response = authenticated_client_member_author.get(
        f"/api/comments/?task={task_todo_medium.pk}",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {comment_task_todo_medium_by_author.pk, comment_task_todo_medium_by_assignee.pk}


@pytest.mark.django_db
def test_list_task_by_not_member(authenticated_client_not_member,
                                 comment_task_by_author,
                                 comment_task_by_assignee,
                                 comment_task_todo_medium_by_author,
                                 comment_task_todo_medium_by_assignee,
                                 task_todo_medium):
    response = authenticated_client_not_member.get(
        f"/api/comments/?task={task_todo_medium.pk}",
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_list_task_invalid_task(authenticated_client_manager,
                                comment_task_by_author,
                                comment_task_by_assignee,
                                comment_task_todo_medium_by_author,
                                comment_task_todo_medium_by_assignee,
                                task):
    response = authenticated_client_manager.get(
        f"/api/comments/?task=9999",
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_list_task_without_task(authenticated_client_manager,
                                comment_task_by_author,
                                comment_task_by_assignee,
                                comment_task_todo_medium_by_author,
                                comment_task_todo_medium_by_assignee,
                                task):
    response = authenticated_client_manager.get(
        f"/api/comments/",
        format="json"
    )

    assert response.status_code == 400

