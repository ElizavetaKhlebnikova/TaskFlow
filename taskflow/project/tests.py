import pytest
from rest_framework.test import APIClient
from .models import Project
from user.models import ProjectMember, Role

from django.contrib.auth.models import User


@pytest.fixture
def user():
    return User.objects.create_user(
        username="Alise",
        password="123456"
    )


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_create_project(user, authenticated_client):

    project_name = "Test project"
    project_description = "my test project"

    response = authenticated_client.post(
        "/api/projects/",
        {
            "name": project_name,
            "description": project_description
        },
        format="json"
    )

    assert response.status_code == 201
    assert Project.objects.count() == 1

    project_id = response.data['id']
    project = Project.objects.get(id=project_id)
    assert project.name == project_name
    assert project.description == project_description
    assert project.owner == user

    project_member = ProjectMember.objects.get(user=user, project=project)
    assert project_member.role == Role.MANAGER


@pytest.mark.django_db
def test_create_project_unauthorised():
    client = APIClient()
    project_name = "Test project"
    project_description = "my test project"

    response = client.post(
        "/api/projects/",
        {
            "name": project_name,
            "description": project_description
        },
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_create_project_ignore_owner(user, authenticated_client):
    other_user = User.objects.create_user(username="Bob", password="123456" )
    project_name = "Test project"
    project_description = "my test project"
    response = authenticated_client.post(
        "/api/projects/",
        {
            "name": project_name,
            "description": project_description,
            "owner": other_user.id
        }, format="json"
    )

    assert response.status_code == 201
    assert Project.objects.count() == 1

    project_id = response.data['id']
    project = Project.objects.get(id=project_id)

    assert project.owner == user
    project_member = ProjectMember.objects.get(project=project, user=user)
    assert project_member.user == user
    assert project_member.role == Role.MANAGER


@pytest.mark.django_db
def test_create_project_transaction_atomic(authenticated_client,
                                           monkeypatch):
    project_name = "Test project"
    project_description = "my test project"

    def fake_create(*args, **kwargs):
        raise RuntimeError("test error")

    monkeypatch.setattr('project.serializers.ProjectMember.objects.create',
                        fake_create)
    with pytest.raises(RuntimeError):
        authenticated_client.post(
            "/api/projects/",
            {
                "name": project_name,
                "description": project_description
            },
            format="json"
        )

    assert Project.objects.count() == 0
    assert ProjectMember.objects.count() == 0
