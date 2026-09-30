import pytest
from rest_framework.test import APIClient
from .models import Project
from user.models import ProjectMember, Role

from django.contrib.auth.models import User


@pytest.fixture
def user_alice():
    return User.objects.create_user(
        username="Alise",
        password="123456"
    )


@pytest.fixture
def user_bob():
    return User.objects.create_user(
        username="Bob",
        password="123456"
    )


@pytest.fixture
def authenticated_client_alice(user_alice):
    client = APIClient()
    client.force_authenticate(user=user_alice)
    return client


@pytest.fixture
def authenticated_client_bob(user_bob):
    client = APIClient()
    client.force_authenticate(user=user_bob)
    return client


@pytest.mark.django_db
def test_get_members_list_invalid_project(authenticated_client_alice):
    response = authenticated_client_alice.get(
        f'/api/project-members/?project=9999',
        format='json'
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_get_members_list(user_alice, user_bob,
                          authenticated_client_alice,
                          authenticated_client_bob):
    project_a = Project.objects.create(name='Test project', description='-')
    project_a_alice = ProjectMember.objects.create(project=project_a, user=user_alice, role=Role.MEMBER)
    project_a_bob = ProjectMember.objects.create(project=project_a, user=user_bob, role=Role.MANAGER)

    project_b = Project.objects.create(name='Test project', description='-')
    project_b_alice = ProjectMember.objects.create(project=project_b, user=user_alice, role=Role.MEMBER)

    project_c = Project.objects.create(name='Test project', description='-')

    response = authenticated_client_alice.get(
        f'/api/project-members/?project={project_a.pk}',
        format='json'
    )
    assert response.status_code == 200
    assert response.data['count'] == 2
    member_ids = {member['id'] for member in response.data['results']}
    assert member_ids == {project_a_alice.pk, project_a_bob.pk}

    response = authenticated_client_alice.get(
        f'/api/project-members/?project={project_b.pk}',
        format='json'
    )
    assert response.status_code == 200
    assert response.data['count'] == 1
    member_ids = {member['id'] for member in response.data['results']}
    assert member_ids == {project_b_alice.pk}

    response = authenticated_client_alice.get(
        f'/api/project-members/?project={project_c.pk}',
        format='json'
    )
    assert response.status_code == 403

    response = authenticated_client_bob.get(
        f'/api/project-members/?project={project_b.pk}',
        format='json'
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_get_members_list_unauthorised():
    project = Project.objects.create(name='Test project', description='-')

    client = APIClient()
    response = client.get(
        f'/api/project-members/?project={project.pk}',
        format='json'
    )
    assert response.status_code == 401
