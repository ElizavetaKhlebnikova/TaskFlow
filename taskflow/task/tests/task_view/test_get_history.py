from datetime import datetime

import pytest
from rest_framework.test import APIClient
from reversion.models import Version
from django.db import connection
from django.test.utils import CaptureQueriesContext


@pytest.mark.django_db
def test_task_history_unauthorised(task_with_history):
    client = APIClient()
    response = client.get(
        f"/api/task/{task_with_history.pk}/history/",
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_task_history_not_member(task_with_history, authenticated_client_not_member):
    response = authenticated_client_not_member.get(
        f"/api/task/{task_with_history.pk}/history/",
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_task_history_invalid_task(authenticated_client_member_author):
    response = authenticated_client_member_author.get(
        f"/api/task/9999/history/",
        format="json"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_task_history_by_author(authenticated_client_member_author, task_with_history, user_member_author):
    response = authenticated_client_member_author.get(
        f"/api/task/{task_with_history.pk}/history/",
        format="json"
    )

    assert response.status_code == 200
    assert len(response.data) == 2
    versions = Version.objects.get_for_object(task_with_history)
    assert response.data[0]['id'] == versions[0].id
    assert response.data[1]['id'] == versions[1].id
    assert response.data[0]['revision'] == versions[0].revision.id
    assert response.data[1]['revision'] == versions[1].revision.id
    assert response.data[0]['user'] == user_member_author.pk
    assert response.data[1]['user'] == user_member_author.pk
    assert datetime.fromisoformat(response.data[0]['date_created']) == versions[0].revision.date_created
    assert datetime.fromisoformat(response.data[1]['date_created']) == versions[1].revision.date_created
    assert response.data[1]['field_dict']['description'] == response.data[0]['field_dict']['description'] == "Description"
    assert response.data[0]['field_dict']['name'] == "Test task 2"
    assert response.data[1]['field_dict']['name'] == "Test task 1"


@pytest.mark.django_db
def test_task_history_by_not_author_or_assignee(authenticated_client_manager, task_with_history, authenticated_client_member_author):
    for _ in range(20):
        authenticated_client_member_author.patch(
            f"/api/task/{task_with_history.pk}/",
            {
                "name": "Test task 2",
            },
            format="json"
        )
    with CaptureQueriesContext(connection) as queries:
        response = authenticated_client_manager.get(
            f"/api/task/{task_with_history.pk}/history/",
            format="json"
        )

    print(f"Количество запросов: {len(queries)}")

    for query in queries:
        print(query["sql"])

    assert response.status_code == 200
    assert len(response.data) == 22
