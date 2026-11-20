import pytest
from django.db.models import Count, F, Prefetch, Q, OuterRef, Subquery
from rest_framework.test import APIClient
from django.db import connection
from django.test.utils import CaptureQueriesContext

from project.models import Project
from task.models import Comment, Task


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
def test_list_comment_by_manager(authenticated_client_manager,
                                 comment_task_by_author,
                                 comment_task_by_assignee,
                                 comment_task_todo_medium_by_author,
                                 comment_task_todo_medium_by_assignee,
                                 task):
    with CaptureQueriesContext(connection) as queries:
        response = authenticated_client_manager.get(
            f"/api/comments/?task={task.pk}",
            format="json"
        )

    print(f"Количество запросов: {len(queries)}")

    for query in queries:
        print(query["sql"])

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {comment_task_by_author.pk, comment_task_by_assignee.pk}


@pytest.mark.django_db
def test_list_comment_20(authenticated_client_manager,
                         user_member_assignee,
                         task):
    for _ in range(20):
        Comment.objects.create(
            task=task,
            author=user_member_assignee,
            text='-'
        )
    with CaptureQueriesContext(connection) as queries:
        response = authenticated_client_manager.get(
            f"/api/comments/?task={task.pk}",
            format="json"
        )

    print(f"Количество запросов: {len(queries)}")

    for query in queries:
        print(query["sql"])

    assert response.status_code == 200
    assert response.data['count'] == 20


@pytest.mark.django_db
def test_list_comment_by_member_assignee(authenticated_client_member_assignee,
                                         comment_task_by_author,
                                         comment_task_by_assignee,
                                         comment_task_todo_medium_by_author,
                                         comment_task_todo_medium_by_assignee,
                                         task_todo_medium,
                                         project):
    response = authenticated_client_member_assignee.get(
        f"/api/comments/?task={task_todo_medium.pk}",
        format="json"
    )
    with CaptureQueriesContext(connection) as queries:
        latest_task = Task.objects.filter(project=OuterRef('pk')).order_by('-created_at')
        projects = Project.objects.annotate(latest_task=Subquery(latest_task.values('created_at')[:1]))

        for project in projects:
            print(project.latest_task)
    print(f"Количество запросов: {len(queries)}")

    for query in queries:
        print(query["sql"])

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {comment_task_todo_medium_by_author.pk, comment_task_todo_medium_by_assignee.pk}


@pytest.mark.django_db
def test_list_comment_by_member_author(authenticated_client_member_author,
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
def test_list_comment_by_not_member(authenticated_client_not_member,
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
def test_list_comment_invalid_task(authenticated_client_manager,
                                   comment_task_by_author,
                                   comment_task_by_assignee,
                                   comment_task_todo_medium_by_author,
                                   comment_task_todo_medium_by_assignee,
                                   task):
    response = authenticated_client_manager.get(
        f"/api/comments/?task=9999",
        format="json"
    )

    print(response.data)
    assert response.status_code == 400


@pytest.mark.django_db
def test_list_comment_invalid_task_string(authenticated_client_manager,
                                          comment_task_by_author,
                                          comment_task_by_assignee,
                                          comment_task_todo_medium_by_author,
                                          comment_task_todo_medium_by_assignee,
                                          task):
    response = authenticated_client_manager.get(
        f"/api/comments/?task=faewf",
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_list_comment_without_task(authenticated_client_manager,
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
