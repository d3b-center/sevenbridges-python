import faker
import pytest

from sevenbridges.errors import SbgError, ResourceNotModified

generator = faker.Factory.create()


def test_get_project(api, given, verifier):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    given.project.exists(id=id)

    # action
    project = api.projects.get(id)

    # verification
    assert project.id == id
    assert project.id in repr(project)
    verifier.project.fetched(id)


@pytest.mark.parametrize("name", [generator.name(), None])
def test_create_project(api, given, verifier, name):
    # preconditions
    project_description = generator.name()
    billing_group = generator.uuid4()
    given.project.can_be_created(
        name=name, billing_group=billing_group, description=project_description
    )

    # action
    if name:
        project = api.projects.create(
            name=name, billing_group=billing_group,
            description=project_description, tags=['test']
        )

        # verification
        assert project.name == name
        assert project.description == project_description
        assert project.billing_group == billing_group

        verifier.project.created()
    else:
        with pytest.raises(SbgError):
            _ = api.projects.create(
                name=name, billing_group=billing_group,
                description=project_description
            )


def test_modify_project(api, given, verifier):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    given.project.exists(id=id)
    new_name = generator.name()
    given.project.can_be_saved(id=id, name=new_name)

    # action
    project = api.projects.get(id)

    # verification
    project.name = new_name
    project.save()
    assert project.name == new_name
    verifier.project.saved(id=project.id)


def test_project_get_members(api, given, verifier):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    given.project.exists(id=id)
    given.member.members_exist(project=id, num_of_members=2)

    # action
    project = api.projects.get(id)
    members = project.get_members()

    assert len(members) == 2
    verifier.member.members_fetched(project=id)


def test_project_add_member(api, given, verifier):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    username = generator.user_name()
    given.project.exists(id=id)
    mocked_member = given.member.member_exist(project=id, username=username)

    # action
    project = api.projects.get(id)
    member = project.add_member(mocked_member['username'],
                                mocked_member['permissions'])
    assert member.username == mocked_member['username']
    assert member.permissions['write'] == mocked_member['permissions']['write']
    assert member.permissions['read'] == mocked_member['permissions']['read']
    assert member.permissions['copy'] == mocked_member['permissions']['copy']
    assert member.permissions['execute'] == mocked_member['permissions'][
        'execute']
    assert member.permissions['admin'] == mocked_member['permissions']['admin']

    # verifier
    verifier.member.member_added(project=id)


def test_project_add_member_email(api, given, verifier):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    email = generator.email()
    given.project.exists(id=id)
    mocked_member = given.member.member_exist(project=id, email=email)

    # action
    project = api.projects.get(id)
    member = project.add_member_email(mocked_member['email'],
                                      mocked_member['permissions'])
    assert member.email == mocked_member['email']
    assert member.permissions['write'] == mocked_member['permissions']['write']
    assert member.permissions['read'] == mocked_member['permissions']['read']
    assert member.permissions['copy'] == mocked_member['permissions']['copy']
    assert member.permissions['execute'] == mocked_member['permissions'][
        'execute']
    assert member.permissions['admin'] == mocked_member['permissions']['admin']

    # verifier
    verifier.member.member_added(project=id)


def test_project_remove_member(api, given, verifier):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    username = generator.user_name()
    given.project.exists(id=id)
    given.member.can_be_removed(id, username)

    # action
    project = api.projects.get(id)
    project.remove_member(username)

    verifier.member.member_removed(id, username)


def test_project_get_files(api, given, verifier):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    given.project.exists(id=id)
    given.file.files_exist_for_project(id, 2)

    # action
    project = api.projects.get(id)
    files = project.get_files()

    assert len(files) == 2
    verifier.file.files_for_project_fetched(id)


def test_projects_get_apps(api, given, verifier):
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    given.project.exists(id=id)
    given.app.apps_exist_for_project(id, 2)

    # action
    project = api.projects.get(id)
    files = project.get_apps()

    assert len(files) == 2
    verifier.app.apps_for_project_fetched(id)


def test_projects_get_tasks(api, given, verifier):
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    given.project.exists(id=id)
    given.task.tasks_exists_for_project(id, 2)

    # action
    project = api.projects.get(id)
    files = project.get_tasks()

    assert len(files) == 2
    verifier.task.tasks_for_project_fetched(id)


def test_member_permissions_save(api, given, verifier):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    username = generator.user_name()
    given.project.exists(id=id)
    mocked_member = given.member.member_exist(project=id, username=username)
    given.member.permissions_can_be_modified(project=id, username=username)

    # action
    project = api.projects.get(id)
    member = project.add_member(mocked_member['username'],
                                mocked_member['permissions'])
    member.permissions['admin'] = True
    member.save()

    assert username in repr(member)

    # verifier
    verifier.member.member_permissions_modified(id, mocked_member['username'])


def test_member_permissions_save_no_changes(api, given, verifier):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    username = generator.user_name()
    given.project.exists(id=id)
    mocked_member = given.member.member_exist(project=id, username=username)
    given.member.permissions_can_be_modified(project=id, username=username)

    # action
    project = api.projects.get(id)
    member = project.add_member(mocked_member['username'],
                                mocked_member['permissions'])

    member.permissions['read'] = True
    with pytest.raises(ResourceNotModified):
        member.save()
