import datetime
import pytest
from rest_framework.test import APIClient
from django.utils import timezone
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
def test_create_project(user_alice, authenticated_client_alice):

    project_name = "Test project"
    project_description = "my test project"

    response = authenticated_client_alice.post(
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
    assert project.owner == user_alice

    project_member = ProjectMember.objects.get(user=user_alice, project=project)
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
def test_create_project_ignore_owner(authenticated_client_alice, user_bob, user_alice):
    project_name = "Test project"
    project_description = "my test project"
    response = authenticated_client_alice.post(
        "/api/projects/",
        {
            "name": project_name,
            "description": project_description,
            "owner": user_bob.id
        }, format="json"
    )

    assert response.status_code == 201
    assert Project.objects.count() == 1

    project_id = response.data['id']
    project = Project.objects.get(id=project_id)

    assert project.owner == user_alice
    project_member = ProjectMember.objects.get(project=project, user=user_alice)
    assert project_member.user == user_alice
    assert project_member.role == Role.MANAGER


@pytest.mark.django_db
def test_create_project_transaction_atomic(authenticated_client_alice,
                                           monkeypatch):
    project_name = "Test project"
    project_description = "my test project"

    def fake_create(*args, **kwargs):
        raise RuntimeError("test error")

    monkeypatch.setattr('project.serializers.ProjectMember.objects.create',
                        fake_create)
    with pytest.raises(RuntimeError):
        authenticated_client_alice.post(
            "/api/projects/",
            {
                "name": project_name,
                "description": project_description
            },
            format="json"
        )

    assert Project.objects.count() == 0
    assert ProjectMember.objects.count() == 0


@pytest.mark.django_db
def test_project_list(authenticated_client_alice, authenticated_client_bob, user_alice, user_bob):
    projects = []
    project_members = []
    for i in range(1, 5):
        if i % 2 == 0:
            user = user_alice
        else:
            user = user_bob
        project = Project(name=f'Test project №{i}', description=f'{i}', owner=user)
        projects.append(project)
        project_members.append(ProjectMember(project=project, user=user))

    Project.objects.bulk_create(projects)
    ProjectMember.objects.bulk_create(project_members)

    assert Project.objects.count() == 4

    response = authenticated_client_alice.get(
        "/api/projects/", format="json"
    )
    assert response.data['count'] == 2
    alice_project_description = {int(project['description']) for project in response.data['results']}
    assert alice_project_description == {2, 4}

    response = authenticated_client_bob.get(
        "/api/projects/", format="json"
    )
    assert response.data['count'] == 2
    bob_project_description = {int(project['description']) for project in response.data['results']}
    assert bob_project_description == {1, 3}


@pytest.mark.django_db
def test_project_list_pagination(authenticated_client_alice, user_alice):
    projects = []
    project_members = []
    for i in range(1, 20):
        project = Project(name=f'Test project №{i}', description=f'{i}', owner=user_alice)
        projects.append(project)
        project_members.append(ProjectMember(project=project, user=user_alice))

    Project.objects.bulk_create(projects)
    ProjectMember.objects.bulk_create(project_members)

    assert Project.objects.count() == 19

    response = authenticated_client_alice.get(
        "/api/projects/", format="json"
    )
    assert len(response.data['results']) == 10
    assert response.data['count'] == 19

    response = authenticated_client_alice.get(
        response.data['next'], format="json"
    )
    assert len(response.data['results']) == 9
    assert response.data['next'] is None


@pytest.mark.django_db
def test_project_list_default_ordering(authenticated_client_alice, user_alice):
    num = 0
    for i in [3, 1, 2]:
        num += 1
        project = Project.objects.create(name=f'Test project №{num}', description=f'{num}', owner=user_alice)
        ProjectMember.objects.create(project=project, user=user_alice)
        Project.objects.filter(id=project.pk).update(
            updated_at=timezone.now() - datetime.timedelta(days=i)
        )

    assert Project.objects.count() == 3

    response = authenticated_client_alice.get(
        "/api/projects/", format="json"
    )
    projects_number = [project['description'] for project in response.data['results']]
    assert projects_number == ['2', '3', '1']


@pytest.mark.django_db
def test_project_list_forbidden_field_ordering(authenticated_client_alice, user_alice):
    num = 0
    for i in [3, 1, 2]:
        num += 1
        project = Project.objects.create(name=f'Test project №{num}', description=f'{num}', owner=user_alice)
        ProjectMember.objects.create(project=project, user=user_alice)
        Project.objects.filter(id=project.pk).update(
            updated_at=timezone.now() - datetime.timedelta(days=i)
        )

    response = authenticated_client_alice.get(
        "/api/projects/?ordering=description", format="json"
    )
    projects_number = [project['description'] for project in response.data['results']]
    assert projects_number == ['2', '3', '1']

    response = authenticated_client_alice.get(
        "/api/projects/?ordering=-description", format="json"
    )
    projects_number = [project['description'] for project in response.data['results']]
    assert projects_number == ['2', '3', '1']


@pytest.mark.django_db
def test_project_list_name_ordering(authenticated_client_alice, user_alice):
    num = 0
    for i in [3, 1, 2]:
        num += 1
        project = Project.objects.create(name=f'Test project №{num}', description=f'{num}', owner=user_alice)
        ProjectMember.objects.create(project=project, user=user_alice)
        Project.objects.filter(id=project.pk).update(
            updated_at=timezone.now() - datetime.timedelta(days=i)
        )

    response = authenticated_client_alice.get(
        "/api/projects/?ordering=name", format="json"
    )
    projects_number = [project['description'] for project in response.data['results']]
    assert projects_number == ['1', '2', '3']

    response = authenticated_client_alice.get(
        "/api/projects/?ordering=-name", format="json"
    )
    projects_number = [project['description'] for project in response.data['results']]
    assert projects_number == ['3', '2', '1']


@pytest.mark.django_db
def test_project_list_updated_at_ordering(authenticated_client_alice, user_alice):
    num = 0
    for i in [3, 1, 2]:
        num += 1
        project = Project.objects.create(name=f'Test project №{num}', description=f'{num}', owner=user_alice)
        ProjectMember.objects.create(project=project, user=user_alice)
        Project.objects.filter(id=project.pk).update(
            updated_at=timezone.now() - datetime.timedelta(days=i)
        )

    response = authenticated_client_alice.get(
        "/api/projects/?ordering=updated_at", format="json"
    )
    projects_number = [project['description'] for project in response.data['results']]
    assert projects_number == ['1', '3', '2']

    response = authenticated_client_alice.get(
        "/api/projects/?ordering=-updated_at", format="json"
    )
    projects_number = [project['description'] for project in response.data['results']]
    assert projects_number == ['2', '3', '1']


@pytest.mark.django_db
def test_project_list_role_filter(authenticated_client_alice, authenticated_client_bob, user_alice, user_bob):
    # Alice member and Bob manager
    project = Project.objects.create(name=f'Test project', description=f'Alice member and Bob manager', owner=user_bob)
    ProjectMember.objects.create(project=project, user=user_alice, role=Role.MEMBER)
    ProjectMember.objects.create(project=project, user=user_bob, role=Role.MANAGER)

    response = authenticated_client_alice.get(
        "/api/projects/?role=member", format="json"
    )
    assert response.data['count'] == 1

    response = authenticated_client_alice.get(
        "/api/projects/?role=manager", format="json"
    )
    assert response.data['count'] == 0

    response = authenticated_client_bob.get(
        "/api/projects/?role=member", format="json"
    )
    assert response.data['count'] == 0

    response = authenticated_client_bob.get(
        "/api/projects/?role=manager", format="json"
    )
    assert response.data['count'] == 1


@pytest.mark.django_db
def test_project_list_role_filter_some_roles(authenticated_client_alice, user_alice):
    # Alice member
    project_a = Project.objects.create(name=f'Test project A', description=f'Alice member', owner=user_alice)
    ProjectMember.objects.create(project=project_a, user=user_alice, role=Role.MEMBER)
    # Alice manager
    project_b = Project.objects.create(name=f'Test project B', description=f'Alice manager', owner=user_alice)
    ProjectMember.objects.create(project=project_b, user=user_alice, role=Role.MANAGER)
    # Alice member
    project_c = Project.objects.create(name=f'Test project C', description=f'Alice member', owner=user_alice)
    ProjectMember.objects.create(project=project_c, user=user_alice, role=Role.MEMBER)

    response = authenticated_client_alice.get(
        "/api/projects/?role=member", format="json"
    )
    assert response.data['count'] == 2
    project_ids = {project['id'] for project in response.data['results']}
    assert project_ids == {project_a.pk, project_c.pk}

    response = authenticated_client_alice.get(
        "/api/projects/?role=manager", format="json"
    )
    assert response.data['count'] == 1
    project_ids = [project['id'] for project in response.data['results']]
    assert project_ids == [project_b.pk]


@pytest.mark.django_db
def test_project_list_role_filter_invalid(authenticated_client_alice):
    response = authenticated_client_alice.get(
        "/api/projects/?role=foo", format="json"
    )
    assert response.status_code == 400


def test_project_list_unauthorised():
    client = APIClient()
    response = client.get(
        "/api/projects/", format="json"
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_project_list_search(authenticated_client_alice, user_alice, user_bob):
    project_google = Project.objects.create(name='my Google', description='-', owner=user_alice)
    ProjectMember.objects.create(project=project_google, user=user_alice, role=Role.MEMBER)

    project_yandex = Project.objects.create(name='my Yandex', description='-', owner=user_alice)
    ProjectMember.objects.create(project=project_yandex, user=user_alice, role=Role.MANAGER)

    project_google_bob = Project.objects.create(name='Bob Google', description='-', owner=user_bob)
    ProjectMember.objects.create(project=project_google_bob, user=user_bob, role=Role.MEMBER)

    response = authenticated_client_alice.get(
        "/api/projects/?search=GOOGLE", format="json"
    )
    assert response.data['count'] == 1
    assert response.data['results'][0]['id'] == project_google.pk

    response = authenticated_client_alice.get(
        "/api/projects/?search=yandex", format="json"
    )
    assert response.data['count'] == 1
    assert response.data['results'][0]['id'] == project_yandex.pk


@pytest.mark.django_db
def test_project_list_search_with_role(authenticated_client_alice, user_alice):
    project_yandex = Project.objects.create(name='my Yandex', description='-', owner=user_alice)
    ProjectMember.objects.create(project=project_yandex, user=user_alice, role=Role.MANAGER)

    response = authenticated_client_alice.get(
        "/api/projects/?search=yandex", format="json"
    )
    assert response.data['count'] == 1
    assert response.data['results'][0]['id'] == project_yandex.pk

    response = authenticated_client_alice.get(
        "/api/projects/?search=yandex&role=member", format="json"
    )
    assert response.data['count'] == 0

    response = authenticated_client_alice.get(
        "/api/projects/?search=yandex&role=manager", format="json"
    )
    assert response.data['count'] == 1
    assert response.data['results'][0]['id'] == project_yandex.pk
