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
def test_get_members_list_without_project(authenticated_client_alice):
    response = authenticated_client_alice.get(
        f'/api/project-members/',
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


@pytest.mark.django_db
def test_create_project_member_unauthorised():
    client = APIClient()
    response = client.post(
        f'/api/project-members/',
        {
            "project": 39,
            "user": 2,
            "role": "member"
        },
        format='json'
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_project_member_by_member(user_alice, user_bob,
                                         authenticated_client_bob):
    project_a = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project_a, user=user_bob, role=Role.MEMBER)
    response = authenticated_client_bob.post(
        f'/api/project-members/',
        {
            "project": project_a.pk,
            "user": user_alice.pk,
            "role": "member"
        },
        format='json'
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_project_member_by_member_with_project_query_param(user_alice, user_bob,
                                         authenticated_client_bob):
    project_a = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project_a, user=user_bob, role=Role.MEMBER)
    project_b = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project_b, user=user_bob, role=Role.MANAGER)
    response = authenticated_client_bob.post(
        f'/api/project-members/?project={project_b.pk}',
        {
            "project": project_a.pk,
            "user": user_alice.pk,
            "role": "member"
        },
        format='json'
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_project_member_by_manager(user_alice, user_bob,
                                          authenticated_client_bob):
    project_a = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project_a, user=user_bob, role=Role.MANAGER)
    response = authenticated_client_bob.post(
        f'/api/project-members/',
        {
            "project": project_a.pk,
            "user": user_alice.pk,
            "role": "member"
        },
        format='json'
    )
    assert response.status_code == 201
    assert response.data['user'] == user_alice.pk
    assert response.data['project'] == project_a.pk


@pytest.mark.django_db
def test_create_project_member_by_not_a_member(user_alice, authenticated_client_bob):
    project_a = Project.objects.create(name='Test project', description='-')
    response = authenticated_client_bob.post(
        f'/api/project-members/',
        {
            "project": project_a.pk,
            "user": user_alice.pk,
            "role": "member"
        },
        format='json'
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_project_member_wrong_project(user_alice, user_bob,
                                             authenticated_client_bob):
    project = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project, user=user_bob, role=Role.MANAGER)
    response = authenticated_client_bob.post(
        f'/api/project-members/',
        {
            "project": 9999,
            "user": user_alice.pk,
            "role": "member"
        },
        format='json'
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_project_member_wrong_user(user_bob,
                                          authenticated_client_bob):
    project = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project, user=user_bob, role=Role.MANAGER)
    response = authenticated_client_bob.post(
        f'/api/project-members/',
        {
            "project": project.pk,
            "user": 9999,
            "role": "member"
        },
        format='json'
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_project_member_duplicate_user(user_alice, user_bob,
                                              authenticated_client_bob):
    project = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project, user=user_bob, role=Role.MANAGER)
    ProjectMember.objects.create(project=project, user=user_alice, role=Role.MEMBER)
    response = authenticated_client_bob.post(
        f'/api/project-members/',
        {
            "project": project.pk,
            "user": user_alice.pk,
            "role": "member"
        },
        format='json'
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_project_member_wrong_role(user_alice, user_bob,
                                          authenticated_client_bob):
    project = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project, user=user_bob, role=Role.MANAGER)
    response = authenticated_client_bob.post(
        f'/api/project-members/',
        {
            "project": project.pk,
            "user": user_alice.pk,
            "role": "123"
        },
        format='json'
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_delete_project_member_unauthorised():
    client = APIClient()
    response = client.delete(
        f'/api/project-members/10/',
        format='json'
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_delete_project_member_by_member(user_bob, user_alice,
                                         authenticated_client_bob):
    project = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project, user=user_bob, role=Role.MEMBER)
    alice = ProjectMember.objects.create(project=project, user=user_alice, role=Role.MEMBER)
    response = authenticated_client_bob.delete(
        f'/api/project-members/{alice.pk}/',
        format='json'
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_project_member_by_not_a_member(user_alice,
                                               authenticated_client_bob):
    project = Project.objects.create(name='Test project', description='-')
    alice = ProjectMember.objects.create(project=project, user=user_alice, role=Role.MEMBER)
    response = authenticated_client_bob.delete(
        f'/api/project-members/{alice.pk}/',
        format='json'
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_project_member_by_manager(user_bob, user_alice,
                                          authenticated_client_bob):
    project = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project, user=user_bob, role=Role.MANAGER)
    alice = ProjectMember.objects.create(project=project, user=user_alice, role=Role.MEMBER)
    response = authenticated_client_bob.delete(
        f'/api/project-members/{alice.pk}/',
        format='json'
    )
    assert response.status_code == 204
    deleted_member = ProjectMember.objects.filter(pk=alice.pk)
    assert deleted_member.exists() is False


@pytest.mark.django_db
def test_delete_project_member_not_found(user_bob, authenticated_client_bob):
    project = Project.objects.create(name='Test project', description='-')
    ProjectMember.objects.create(project=project, user=user_bob, role=Role.MANAGER)
    response = authenticated_client_bob.delete(
        f'/api/project-members/999/',
        format='json'
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_project_member_oneself(user_bob, authenticated_client_bob):
    project = Project.objects.create(name='Test project', description='-')
    member = ProjectMember.objects.create(project=project, user=user_bob, role=Role.MANAGER)
    response = authenticated_client_bob.delete(
        f'/api/project-members/{member.pk}/',
        format='json'
    )
    assert response.status_code == 204
