import pytest


@pytest.mark.django_db
def test_list_task_by_manager(authenticated_client_manager,
                              project,
                              task_todo_medium,
                              task_todo_high,
                              task_planed_high_author_is_assignee):
    response = authenticated_client_manager.get(
        f"/api/task/?project={project.pk}",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 3


@pytest.mark.django_db
def test_list_task_by_member_author(authenticated_client_member_author,
                                    project,
                                    task_todo_medium,
                                    task_todo_high,
                                    task_planed_high_author_is_assignee):
    response = authenticated_client_member_author.get(
        f"/api/task/?project={project.pk}",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 3


@pytest.mark.django_db
def test_list_task_by_member_assignee(authenticated_client_member_assignee,
                                      project,
                                      task_todo_medium,
                                      task_todo_high,
                                      task_planed_high_author_is_assignee):
    response = authenticated_client_member_assignee.get(
        f"/api/task/?project={project.pk}",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 3


@pytest.mark.django_db
def test_list_task_without_project(authenticated_client_member_author,
                                   task_todo_medium,
                                   task_todo_high,
                                   task_planed_high_author_is_assignee):
    response = authenticated_client_member_author.get(
        f"/api/task/",
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_list_task_with_status_filter(authenticated_client_manager,
                                      project,
                                      task_todo_medium,
                                      task_todo_high,
                                      task_planed_high_author_is_assignee
                                      ):
    response = authenticated_client_manager.get(
        f"/api/task/?project={project.pk}&status=todo",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {task_todo_medium.pk, task_todo_high.pk}


@pytest.mark.django_db
def test_list_task_with_priority_filter(authenticated_client_manager,
                                        project,
                                        task_todo_medium,
                                        task_todo_high,
                                        task_planed_high_author_is_assignee
                                        ):
    response = authenticated_client_manager.get(
        f"/api/task/?project={project.pk}&priority=high",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {task_todo_high.pk, task_planed_high_author_is_assignee.pk}


@pytest.mark.django_db
def test_list_task_with_assignee_filter(authenticated_client_manager,
                                        project,
                                        task_todo_medium,
                                        task_todo_high,
                                        task_planed_high_author_is_assignee,
                                        user_member_assignee):
    response = authenticated_client_manager.get(
        f"/api/task/?project={project.pk}&assignee={user_member_assignee.pk}",
        format="json"
    )

    assert response.status_code == 200
    assert response.data['count'] == 2
    task_ids = {task['id'] for task in response.data['results']}
    assert task_ids == {task_todo_medium.pk, task_todo_high.pk}


@pytest.mark.django_db
def test_list_task_invalid_project(authenticated_client_not_member):
    response = authenticated_client_not_member.get(
        f"/api/task/?project=9999",
        format="json"
    )

    assert response.status_code == 400
