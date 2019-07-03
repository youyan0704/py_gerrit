# -*- coding: utf-8 -*-
# @Time    : 19-5-9 上午11:27
# @Author  : allen.you
from __future__ import absolute_import
import logging

import requests
from requests.auth import HTTPBasicAuth

from py_gerrit.models.branch import Branch
from py_gerrit.models.plugin import Plugin
from py_gerrit.models.group import Group, GroupDetail
from py_gerrit.models.user import User
from py_gerrit.models.project import Project
from py_gerrit.utils.util import _decode_response, decode_model, decode_model_from_list, decode_model_from_json
from py_gerrit.config import HEADERS

log = logging.getLogger(__name__)


class ResetApi(object):

    def __init__(self, url, username, password):
        self.kwargs = {
            'auth': HTTPBasicAuth(username, password),
            'headers': HEADERS
        }
        self.url = url.rstrip('/')

        if not self.url.endswith('/'):
            self.url += '/'
        self.session = requests.Session()

    def make_url(self, endpoint):
        endpoint = endpoint.lstrip('/')
        return self.url + endpoint + '/'

    def _login(self):
        self.get('login')
        self.kwargs['headers'].update({
            'Cookie': self.kwargs['headers']['Cookie'] + '; ' + '; '.join(
                '='.join([key, value]) for key, value in self.session.cookies.items())
        })

        self.kwargs.pop('auth')

    def get(self, endpoint, **kwargs):
        kwargs.update(self.kwargs.copy())
        response = self.session.get(self.make_url(endpoint), **kwargs)
        return _decode_response(response)

    def put(self, endpoint, data):
        if self.session.cookies.get('XSRF_TOKEN'):
            self.kwargs["headers"].update(
                {"x-gerrit-auth": self.session.cookies.get('XSRF_TOKEN')})
        response = self.session.put(self.make_url(endpoint), data=data)
        return _decode_response(response)

    def post(self, endpoint, data):
        self.kwargs["headers"].update(
            {"Content-Type": "application/json;charset=utf-8"})
        response = self.session.post(self.make_url(endpoint), data=data)
        return _decode_response(response)

    def delete(self, endpoint, **kwargs):
        kwargs.update(self.kwargs.copy())
        response = self.session.delete(self.make_url(endpoint), **kwargs)
        return _decode_response(response)


class GerritRestApi(ResetApi):

    def __init__(self, url, username, password):
        super().__init__(url, username, password)
        self._login()

    def documentation(self, **kwargs):
        """With q parameter, search our documentation index for the terms."""

        self.get('/Documentation', params=kwargs)

    def projects(self, **kwargs):
        """
            Lists the projects accessible by the caller. This is the same as using the ls-projects command over SSH, and accepts the same options as query parameters.
            Branch(b)  Limit the results to the projects having the specified branch and include the sha1 of the branch in the results.
            Limit(n)   Limit the number of projects to be included in the results.
            Prefix(p)  Limit the results to those projects that start with the specified prefix.The match is case sensitive. May not be used together with m or r.
            Regex(r)   Limit the results to those projects that match the specified regex.
            Skip(S)    Skip the given number of projects from the beginning of the list.
            Substring(m) Limit the results to those projects that match the specified substring.
            Tree(t)    Get projects inheritance in a tree-like format. This option does not work together with the branch option.
            Type(type) Get projects with specified type: ALL, CODE, PERMISSIONS.
            All        Get all projects, including those whose state is "HIDDEN". May not be used together with the state option.
            State(s)   Get all projects with the given state. May not be used together with the all option.
            and so on....
        """
        return self.get('projects', params=kwargs)

    def project_info(self, project, **kwargs):
        """
            Retrieves a project.
        """
        return self.get('projects/%s' % project, params=kwargs)

    def create_project(self, project, **kwargs):
        """
            Creates a new project. In the request body additional data for the project can be provided as ProjectInput.
            eg. {
                    "description": "This is a demo project.",
                    "submit_type": "INHERIT",
                    "owners": [
                      "MyProject-Owners"
                    ]
                  }
        """
        # 默认创建空提交
        data = {'create_empty_commit': 'true'}
        data.update(kwargs)

        return self.put('projects/%s' % project, data)

    def get_project_description(self, project, **kwargs):
        """Retrieves the description of a project."""

        return self.get('projects/%s/description' % project, params=kwargs)

    def set_project_description(self, project, description, **kwargs):
        """Sets the description of a project.
        eg. {
                "description": "Plugin for Gerrit that handles the replication.",
                "commit_message": "Update the project description"
            }
        """

        data = {'description': description}
        data.update(kwargs)

        return self.put('projects/%s/description' % project, data)

    def delete_project_description(self, project, **kwargs):
        """Deletes the description of a project."""

        return self.delete('projects/%s/description' % project, **kwargs)

    def get_project_parent(self, project, **kwargs):
        """Retrieves the name of a project’s parent project. For the All-Projects root project an empty string is returned."""

        return self.get('projects/%s/parent' % project, params=kwargs)

    def set_project_parent(self, project, parent, **kwargs):
        """Sets the parent project for a project.
        eg. {
                "parent": "Public-Plugins",
                "commit_message": "Update the project parent"
              }
        """

        data = {'parent': parent}
        data.update(kwargs)

        return self.put('projects/%s/parent' % project, data)

    def get_project_head(self, project, **kwarg):
        """Retrieves for a project the name of the branch to which HEAD points."""

        return self.get('projects/%s/HEAD' % project, params=kwarg)

    def set_project_head(self, project, head, **kwarg):
        """Sets HEAD for a project.
            eg. {
                "ref": "refs/heads/stable"
              }
        """

        data = {'ref': head}
        data.update(kwarg)

        return self.put('projects/%s/HEAD' % project, data)

    def get_repository_statistics(self, project, **kwargs):
        """Return statistics for the repository of a project."""

        return self.get('/projects/%s/statistics.git' % project, params=kwargs)

    def get_project_config(self, project, **kwargs):
        """
            Gets some configuration information about a project.
            Note that this config info is not simply the contents of project.config;
            it generally contains fields that may have been inherited from parent projects.
        """
        return self.get('projects/%s/config' % project, params=kwargs)

    def set_project_config(self, project, config, **kwargs):
        """Sets the configuration of a project.
            eg. {
                    "description": "demo project",
                    "use_contributor_agreements": "FALSE",
                    "use_content_merge": "INHERIT",
                    "use_signed_off_by": "INHERIT",
                    "create_new_change_for_all_not_in_target": "INHERIT",
                    "enable_signed_push": "INHERIT",
                    "require_signed_push": "INHERIT",
                    "reject_implicit_merges": "INHERIT",
                    "require_change_id": "TRUE",
                    "max_object_size_limit": "10m",
                    "submit_type": "REBASE_IF_NECESSARY",
                    "state": "ACTIVE"
                  }
        """

        data = config
        data.update(kwargs)

        return self.put('projects/%s/config' % project, data)

    def run_gc(self, project, **kwargs):
        """Run the Git garbage collection for the repository of a project.
            eg. {
                    "show_progress": true
                    "async": true
                  }
        """

        return self.post('/projects/%s/gc' % project, kwargs)

    def ban_commit(self, project, commits, **kwargs):
        """ Marks commits as banned for the project.
            If a commit is banned Gerrit rejects every push that includes this commit with contains banned commit …​.
            eg. {
                    "commits": [
                      "a8a477efffbbf3b44169bb9a1d3a334cbbd9aa96",
                      "cf5b56541f84b8b57e16810b18daca9c3adc377b"
                    ],
                    "reason": "Violates IP"
                  }
        """
        data = {'commits': commits}
        data.update(kwargs)
        return self.put('/projects/%s/ban' % project, data)

    def get_project_access(self, project, **kwargs):
        """
            Lists the access rights for a single project.
        """

        return self.get('/projects/%s/access' % project, params=kwargs)

    def set_project_access(self, project, **kwargs):
        """Add, Update and Delete Access Rights for Project
            eg.{
                "remove": {
                  "refs/*": {
                    "permissions": {
                      "read": {
                        "rules": {
                          "c2ce4749a32ceb82cd6adcce65b8216e12afb41c": {
                            "action": "ALLOW"
                          }
                        }
                      }
                    }
                  }
                }
              }
        """

        return self.post('/projects/%s/access' % project, kwargs)

    def create_access_changes_for_review(self, project, **kwargs):
        """Sets access rights for the project using the diff schema provided by ProjectAccessInput.
            Sets access rights for the project using the diff schema provided by ProjectAccessInput
            eg.  {
                    "add": {
                      "refs/heads/*": {
                        "permissions": {
                          "read": {
                            "rules": {
                              "global:Anonymous-Users": {
                                "action": "DENY",
                                "force": false
                              }
                            }
                          }
                        }
                      }
                    }
                  }
        """

        return self.put('/projects/%s/access:review' % project, kwargs)

    def check_access(self, project, **kwargs):
        """ This command runs access checks for other users. This requires the View Access global capability."""

        return self.get('/projects/%s/check.access' % project, params=kwargs)

    def index_project(self, project, **kwargs):
        """
            Adds or updates the current project (and children, if specified) in the secondary index.
            The indexing task is executed asynchronously in background and this command returns immediately if async is specified in the input.
            As an input, a IndexProjectInput entity can be provided.
            eg. {
                    "index_children": "true"
                    "async": "true"
                  }
        """

        return self.post('/projects/%s/index' % project, kwargs)

    def index_all_changes_project(self, project):
        """
            Adds or updates all the changes belonging to a project in the secondary index.
            The indexing task is executed asynchronously in background, so this command returns immediately.
        """

        return self.put('/projects/%s/index.changes' % project)

    def check_project_consistency(self, project, **kwargs):
        """ Performs consistency checks on the project.
            Which consistency checks should be performed is controlled by the CheckProjectInput entity in the request body.
            eg.{
                "auto_closeable_changes_check": {
                  "fix": true,
                  "branch": "refs/heads/master",
                  "max_commits": 100
                }
              }
        """

        return self.post('/projects/%s/check' % project, kwargs)

    def delete_project(self, project, **kwargs):
        """
            删除项目, 此方法需要安装delete-project 插件.
            eg. {
                    'force': 'true'
                    'preserve': 'true'
                }
        """

        data = {'force': 'true', 'preserve': 'true'}
        data.update(kwargs)
        return self.post('projects/%s/delete-project~delete' % project, data)

    def branches(self, project, **kwargs):
        """
            List the branches of a project.
            Limit(n)  Limit the number of branches to be included in the results.
            Skip(S)   Skip the given number of branches from the beginning of the list.
            Substring(m)  Limit the results to those branches that match the specified substring.
            Regex(r)  Limit the results to those branches that match the specified regex. Boundary matchers '^' and '$' are implicit.
                        For example: the regex 't*' will match any branches that start with 't' and regex '*t' will match any branches that end with 't'.

        """
        branches = self.get('projects/%s/branches' % project, params=kwargs)

        return branches

    def get_branch(self, project, branch, **kwargs):
        """
            Retrieves a branch of a project.
            eg. /projects/work%2Fmy-project/branches/master
        """
        return self.get('/projects/%s/branches/%s' % (project, branch), params=kwargs)

    def create_branch(self, project, branch, **kwargs):
        """
            Creates a new branch.
            eg. {
                    "revision": "76016386a0d8ecc7b6be212424978bb45959d668"
                  }
        """
        data = {'revision': 'master'}
        data.update(kwargs)
        return self.put('projects/%s/branches/%s' % (project, branch), data)

    def delete_branch(self, project, branch, **kwargs):
        """
            Deletes a branch.
        """
        return self.delete('projects/%s/branches/%s' % (project, branch), **kwargs)

    def delete_branches(self, project, branches, **kwargs):
        """
            Delete one or more branches.
        """

        data = {'branches': branches}
        data.update(kwargs)
        return self.put('projects/%s/branches/branches:delete' % project, data)

    def get_content(self, project, branch, file, **kwargs):
        """Gets the content of a file from the HEAD revision of a certain branch."""

        return self.get('/projects/%s/branches/%s/files/%s/content' % (project, branch, file), params=kwargs)

    def get_mergeable_information(self, project, branch, **kwargs):
        """Gets whether the source is mergeable with the target branch."""

        return self.get('/projects/%s/branches/%s/mergeable' % (project, branch), params=kwargs)

    def get_reflog(self, project, branch, **kwargs):
        """ Gets the reflog of a certain branch.
            The caller must be project owner.
        """
        return self.get('/projects/%s/branches/%s/reflog' % (project, branch), params=kwargs)

    def ls_child_projects(self, project, **kwargs):
        """List the direct child projects of a project."""

        return self.get('/projects/%s/children/' % project, params=kwargs)

    def get_child_projects(self, project, child_project, **kwargs):
        """Retrieves a child project. If a non-direct child project should be retrieved the parameter recursive must be set."""

        return self.get('/projects/%s/children/%s' % (project, child_project), params=kwargs)

    def create_tag(self, project, tag, **kwargs):
        """Create a new tag on the project.
            eg. {
                "message": "annotation",
                "revision": "c83117624b5b5d8a7f86093824e2f9c1ed309d63"
              }
        """

        return self.put('/projects/%s/tags/%s' % (project, tag), kwargs)

    def ls_tags(self, project, **kwargs):
        """List the tags of a project."""

        return self.get('/projects/%s/tags/' % project, params=kwargs)

    def get_tag(self, project, tag, **kwargs):
        """Retrieves a tag of a project."""

        return self.get('/projects/%s/tags/%s' % (project, tag), params=kwargs)

    def delete_tag(self, project, tag, **kwargs):
        """Deletes a tag."""

        return self.delete('/projects/%s/tags/%s' % (project, tag), **kwargs)

    def delete_tags(self, project, tags, **kwargs):
        """Delete one or more tags.
            eg. {
                "tags": [
                  "v1.0",
                  "v2.0"
                ]
              }
        """
        data = {'tags': tags}
        data.update(kwargs)
        return self.post('/projects/%s/tags:delete' % project, data)

    def get_commit(self, project, commit, **kwargs):
        """Retrieves a commit of a project."""

        return self.get('/projects/%s/commits/%s' % (project, commit), params=kwargs)

    def get_include_in_commit(self, project, commit, **kwargs):
        """Retrieves the branches and tags in which a change is included. As result an IncludedInInfo entity is returned."""

        return self.get('/projects/%s/commits/%s/in' % (project, commit), params=kwargs)

    def get_content_from_commit(self, project, commit, file, **kwargs):
        """Gets the content of a file from a certain commit."""

        return self.get('/projects/%s/commits/%s/files/%s/content' % (project, commit, file), params=kwargs)

    def cherry_pick_commit(self, project, commit, destination, message, **kwargs):
        """Cherry-picks a commit of a project to a destination branch.
            eg. {
                    "message" : "Implementing Feature X",
                    "destination" : "release-branch"
                  }
        """
        data = {
            "message": message,
            "destination": destination
        }
        data.update(kwargs)

        return self.post('/projects/%s/commits/%s/cherrypick' % (project, commit), data)

    def ls_commit_files(self, project, commit, **kwargs):
        """Lists the files that were modified, added or deleted in a commit."""

        return self.get('/projects/%s/commits/%s/files' % (project, commit), params=kwargs)

    def ls_dashboards(self, project, **kwargs):
        """List custom dashboards for a project."""

        return self.get('/projects/%s/dashboards' % project, params=kwargs)

    def get_dashboards(self, project, dashboard, **kwargs):
        """Retrieves a project dashboard. The dashboard can be defined on that project or be inherited from a parent project."""

        return self.get('/projects/%s/dashboards/%s' % (project, dashboard), params=kwargs)

    def set_dashboard(self, project, dashboard, **kwargs):
        """ Updates/Creates a project dashboard.
            Currently only supported for the default dashboard.
            eg. {
                    "id": "main:closed",
                    "commit_message": "Define the default dashboard"
                  }
        """

        self.put('/projects/%s/dashboards/%s' % (project, dashboard), kwargs)

    def delete_dashboard(self, project, dashboard, **kwargs):
        """ Deletes a project dashboard.
            Currently only supported for the default dashboard.
        """
        self.delete('/projects/%s/dashboards/%s' % (project, dashboard), **kwargs)

    def plugins(self, **kwargs):
        """
            Lists the plugins installed on the Gerrit server. Only the enabled plugins are returned unless the all option is specified.
        """
        return self.get('plugins', params=kwargs)

    def install_plugin(self, plugin, url, **kwargs):
        """Installs a new plugin on the Gerrit server.
        If a plugin with the specified name already exists it is overwritten.
        Note: if the plugin provides its own name in the MANIFEST file,
        then the plugin name from the MANIFEST file has precedence over the {plugin-id} above.
        eg. {
                "url": "file:///gerrit/plugins/delete-project/delete-project-2.8.jar"
              }
        """
        data = {'url': url}
        data.update(kwargs)

        return self.put('/plugins/%s' % plugin, data)

    def get_plugin_status(self, plugin, **kwargs):
        """Retrieves the status of a plugin on the Gerrit server."""

        return self.get('/plugins/%s/gerrit~status' % plugin, params=kwargs)

    def enable_plugin(self, plugin, **kwargs):
        """Enables a plugin on the Gerrit server."""

        return self.post('/plugins/%s/gerrit~disable' % plugin, **kwargs)

    def disable_plugin(self, plugin, **kwargs):
        """Disables a plugin on the Gerrit server."""

        return self.post('/plugins/%s/gerrit~enable' % plugin, **kwargs)

    def reload_plugin(self, plugin, **kwargs):
        """Reloads a plugin on the Gerrit server."""

        return self.post('/plugins/%s/gerrit~reload' % plugin, **kwargs)

    def groups(self, **kwargs):
        """Lists the groups accessible by the caller. This is the same as using the ls-groups command over SSH, and accepts the same options as query parameters."""

        return self.get('/groups', params=kwargs)

    def get_group(self, group_id, **kwargs):
        """Retrieves a group."""

        self.get('/groups/%s' % group_id, params=kwargs)

    def create_group(self, group_name, **kwargs):
        """Creates a new Gerrit internal group."""

        self.put('/groups/%s' % group_name, **kwargs)

    def get_group_detail(self, group_id, **kwargs):
        """Retrieves a group with the direct members and the directly included groups."""

        self.get('/groups/%s/detail' % group_id, params=kwargs)

    def get_group_name(self, group_id, **kwargs):
        """Retrieves the name of a group."""

        return self.get('/groups/%s/name' % group_id, params=kwargs)

    def rename_group(self, group_id, group_name, **kwargs):
        """Renames a Gerrit internal group."""

        data = {'name': group_name}
        data.update(kwargs)

        self.put('/groups/%s/name' % group_id, data)

    def get_group_description(self, group_id, **kwargs):
        """Retrieves the description of a group."""

        self.get('/groups/%s/description' % group_id, params=kwargs)

    def set_group_description(self, group_id, description, **kwargs):
        """Sets the description of a Gerrit internal group."""

        data = {'description': description}
        data.update(kwargs)

        return self.put('/groups/%s/description' % group_id, data)

    def delete_group_description(self, group_id, **kwargs):
        """Deletes the description of a Gerrit internal group."""

        return self.delete('/groups/%s/description' % group_id, **kwargs)

    def get_group_options(self, group_id, **kwargs):
        """Retrieves the options of a group."""

        return self.get('/groups/%s/options' % group_id, params=kwargs)

    def set_group_options(self, group_id, **kwargs):
        """Sets the options of a Gerrit internal group.
        eg.{
            "visible_to_all": true
          }
        """

        return self.put('/groups/%s/options' % group_id, **kwargs)

    def get_group_owner(self, group_id, **kwargs):
        """Retrieves the owner group of a Gerrit internal group."""

        return self.get('/groups/%s/owner' % group_id, params=kwargs)

    def set_group_owner(self, group_id, owner, **kwargs):
        """Sets the owner group of a Gerrit internal group.
        eg.{
            "owner": "6a1e70e1a88782771a91808c8af9bbb7a9871389"
          }
        """
        data = {'owner': owner}
        data.update(kwargs)

        return self.put('/groups/%s/owner' % group_id, data)

    def get_audit_log(self, group_id, **kwargs):
        """Gets the audit log of a Gerrit internal group."""

        return self.get('/groups/%s/log.audit' % group_id, params=kwargs)

    def index_group(self, group_id, **kwargs):
        """Adds or updates the internal group in the secondary index."""

        return self.post('/groups/%s/index' % group_id, **kwargs)


    def group_members(self, group, **kwargs):
        """Lists the direct members of a Gerrit internal group."""

        return self.get('/groups/%s/members' % group, params=kwargs)

    def get_group_member(self, group, member, **kwargs):
        """Retrieves a group member."""
        return self.get('/groups/%s/members/%s' % (group, member), params=kwargs)

    def add_group_member(self, group, member, **kwargs):
        """Adds a user as member to a Gerrit internal group."""

        return self.put('/groups/%s/members/%s' % (group, member), **kwargs)

    def add_group_members(self, group, members, **kwargs):
        """Adds a user as member to a Gerrit internal group.
        eg.
            {
            "members": [
              "jane.roe@example.com",
              "john.doe@example.com"
            ]
          }
        """
        data = {'members': members}
        data.update(kwargs)

        return self.post('/groups/%s/members.add' % group, data)

    def remove_group_member(self, group, member, **kwargs):
        """Removes a user from a Gerrit internal group."""

        return self.delete('/groups/%s/members/%s' % (group, member), **kwargs)

    def remove_group_members(self, group, members, **kwargs):
        """Removes one or several users from a Gerrit internal group.
        eg.
            {
            "members": [
              "jane.roe@example.com",
              "john.doe@example.com"
            ]
          }
        """
        data = {'members': members}
        data.update(kwargs)

        return self.post('/groups/%s/members.delete' % group, data)

    def subgroups(self, group, **kwargs):
        """Lists the direct subgroups of a group."""

        return self.get('/groups/%s/groups' % group, params=kwargs)

    def get_subgroup(self, group, subgroup, **kwargs):
        """Retrieves a subgroup."""

        return self.get('/groups/%s/groups/%s' % (group, subgroup), params=kwargs)

    def add_subgroup(self, group, subgroup, **kwargs):
        """Adds an internal or external group as subgroup to a Gerrit internal group. External groups must be specified using the UUID."""

        return self.put('/groups/%s/groups/%s' % (group, subgroup), **kwargs)

    def add_subgroups(self, group, subgroups, **kwargs):
        """Adds one or several groups as subgroups to a Gerrit internal group.
        eg.
            {
            "groups": [
              "MyGroup",
              "MyOtherGroup"
            ]
          }
        """
        data = {'groups': subgroups}
        data.update(kwargs)

        return self.put('/groups/%s/groups' % group, data)

    def remove_subgroup(self, group, subgroup, **kwargs):
        """Removes a subgroup from a Gerrit internal group."""

        return self.delete('/groups/%s/groups/%s' % (group, subgroup), **kwargs)

    def remove_subgroups(self, group, subgroups, **kwargs):
        """Removes one or several subgroups from a Gerrit internal group.
        eg.
            {
            "groups": [
              "MyGroup",
              "MyOtherGroup"
            ]
          }
        """
        data = {'groups': subgroups}
        data.update(kwargs)

        return self.post('/groups/%s/groups.delete' % group, data)


    def accounts(self, **kwargs):
        """Queries accounts visible to the caller. The query string must be provided by the q parameter.
            The n parameter can be used to limit the returned results."""

        return self.get('/accounts', params=kwargs)

    def get_account(self, account, **kwargs):
        """Returns an account as an AccountInfo entity."""

        return self.get('/accounts/%s' % account, params=kwargs)

    def create_account(self, username, **kwargs):
        """Creates a new account.
            eg. {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "ssh_key": "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA0T...YImydZAw==",
                    "http_password": "19D9aIn7zePb",
                    "groups": [
                      "MyProject-Owners"
                    ]
                  }
        """
        return self.put('/accounts/%s' % username, **kwargs)

    def get_account_detail(self, account, **kwargs):
        """Retrieves the details of an account as an AccountDetailInfo entity."""

        return self.get('/accounts/%s/detail' % account, params=kwargs)

    def get_account_name(self, account, **kwargs):
        """Retrieves the full name of an account."""

        return self.get('/accounts/%s/name' % account, params=kwargs)

    def set_account_name(self, account, name, **kwargs):
        """Sets the full name of an account."""
        data = {'name': name}
        data.update(kwargs)

        return self.put('/accounts/%s/name' % account, data)

    def delete_account_name(self, account, **kwargs):
        """Deletes the name of an account."""

        return self.delete('/accounts/%s/name' % account, **kwargs)

    def get_account_status(self, account, **kwargs):
        """Retrieves the status of an account."""

        return self.get('/accounts/%s/status' % account, params=kwargs)

    def set_account_status(self, account, **kwargs):
        """Sets the status of an account.
            eg. {
                    "status": "Out Of Office"
                  }
        """

        return self.put('/accounts/%s/status' % account, **kwargs)

    def get_username(self, account, **kwargs):
        """Retrieves the username of an account."""

        return self.get('/accounts/%s/username' % account, params=kwargs)

    def set_username(self, account, username, **kwargs):
        """Sets the username of an account."""

        data = {'username': username}
        data.update(kwargs)

        return self.put('/accounts/%s/username' % account, data)

    def get_active(self, account, **kwargs):
        """Checks if an account is active."""

        return self.get('/accounts/%s/active' % account, params=kwargs)

    def set_active(self, account, **kwargs):
        """Sets the account state to active."""

        return self.put('/accounts/%s/active' % account, **kwargs)

    def delete_active(self, account, **kwargs):
        """Sets the account state to inactive."""

        return self.delete('/accounts/%s/active' % account, **kwargs)

    def generate_http_password(self, account, **kwargs):
        """Sets/Generates the HTTP password of an account."""

        return self.put('/accounts/%s/password.http' % account, **kwargs)

    def delete_http_password(self, account, **kwargs):
        """Deletes the HTTP password of an account."""

        return self.delete('/accounts/%s/password.http' % account, **kwargs)

    def get_oauthtoken(self, account, **kwargs):
        """Returns a previously obtained OAuth access token."""

        return self.get('/accounts/%s/oauthtoken' % account, params=kwargs)

    def get_account_emails(self, account, **kwargs):
        """Returns the email addresses that are configured for the specified user."""

        return self.get('/accounts/%s/emails' % account, params=kwargs)

    def get_account_email(self, account, email, **kwargs):
        """Retrieves an email address of a user."""

        return self.get('/accounts/%s/emails/%s' % (account, email), params=kwargs)

    def create_account_email(self, account, email, **kwargs):
        """ Registers a new email address for the user.
            A verification email is sent with a link that needs to be visited to confirm the email address,
            unless DEVELOPMENT_BECOME_ANY_ACCOUNT is used as authentication type.
            For the development mode email addresses are directly added without confirmation.
            A Gerrit administrator may add an email address without confirmation by setting no_confirmation in the EmailInput.
            If sendemail.allowrcpt is configured, the added email address must belong to a domain that is allowed, unless no_confirmation is set."""

        return self.put('/accounts/%s/emails/%s' % (account, email), **kwargs)

    def delete_account_email(self, account, email, **kwargs):
        """Deletes an email address of an account."""

        return self.delete('/accounts/%s/emails/%s' % (account, email), **kwargs)

    def set_preferred_email(self, account, email, **kwargs):
        """Sets an email address as preferred email address for an account."""

        return self.put('/accounts/%s/emails/%s/preferred' % (account, email), **kwargs)


    def list_ssh_keys(self, account, **kwargs):
        """Returns the SSH keys of an account."""

        return self.get('/accounts/%s/sshkeys' % account, params=kwargs)

    def get_ssh_key(self, account, ssh_key, **kwargs):
        """Retrieves an SSH key of a user."""

        return self.get('/accounts/%s/sshkeys/%s' % (account, ssh_key), params=kwargs)

    def add_ssh_key(self, account, ssh_key):
        """Adds an SSH key for a user.
            The SSH public key must be provided as raw content in the request body.
        """
        headers = {'Content-Type': 'plain/text'}

        return self.session.post('/accounts/%s/sshkeys' % account, data=ssh_key, headers=headers)

    def delete_ssh_key(self, account, ssh_key, **kwargs):
        """Deletes an SSH key of a user."""

        return self.delete('/accounts/%s/sshkeys/%s' % (account, ssh_key), params=kwargs)

    def list_gpgkeys(self, account, **kwargs):
        """Returns the GPG keys of an account."""

        return self.get('/accounts/%s/gpgkeys' % account, params=kwargs)

    def get_gpgkey(self, account, gpgkey, **kwargs):
        """Retrieves a GPG key of a user."""

        return self.get('/accounts/%s/gpgkeys/%s' % (account, gpgkey), **kwargs)

    def add_or_delete_gpgkey(self, account, **kwargs):
        """Add or delete one or more GPG keys for a user.
            eg. {
                "add": [
                  "-----BEGIN PGP PUBLIC KEY BLOCK-----\nVersion: GnuPG v1\n\nmQENBFXUpNcBCACv4paCiyKxZ0EcKy8VaWVNkJlNebRBiyw9WxU85wPOq5Gz/3GT\nRQwKqeY0SxVdQT8VNBw2sBe2m6eqcfZ2iKmesSlbXMe15DA7k8Bg4zEpQ0tXNG1L\nhceZDVQ1Xk06T2sgkunaiPsXi82nwN3UWYtDXxX4is5e6xBNL48Jgz4lbqo6+8D5\nvsVYiYMx4AwRkJyt/oA3IZAtSlY8Yd445nY14VPcnsGRwGWTLyZv9gxKHRUppVhQ\nE3o6ePXKEVgmONnQ4CjqmkGwWZvjMF2EPtAxvQLAuFa8Hqtkq5cgfgVkv/Vrcln4\nnQZVoMm3a3f5ODii2tQzNh6+7LL1bpqAmVEtABEBAAG0H0pvaG4gRG9lIDxqb2hu\nLmRvZUBleGFtcGxlLmNvbT6JATgEEwECACIFAlXUpNcCGwMGCwkIBwMCBhUIAgkK\nCwQWAgMBAh4BAheAAAoJEJNQnkuvyKSbfjoH/2OcSQOu1kJ20ndjhgY2yNChm7gd\ntU7TEBbB0TsLeazkrrLtKvrpW5+CRe07ZAG9HOtp3DikwAyrhSxhlYgVsQDhgB8q\nG0tYiZtQ88YyYrncCQ4hwknrcWXVW9bK3V4ZauxzPv3ADSloyR9tMURw5iHCIeL5\nfIw/pLvA3RjPMx4Sfow/bqRCUELua39prGw5Tv8a2ZRFbj2sgP5j8lUFegyJPQ4z\ntJhe6zZvKOzvIyxHO8llLmdrImsXRL9eqroWGs0VYqe6baQpY6xpSjbYK0J5HYcg\nTO+/u80JI+ROTMHE6unGp5Pgh/xIz6Wd34E0lWL1eOyNfGiPLyRWn1d0yZO5AQ0E\nVdSk1wEIALUycrH2HK9zQYdR/KJo1yJJuaextLWsYYn881yDQo/p06U5vXOZ28lG\nAq/Xs96woVZPbgME6FyQzhf20Z2sbr+5bNo3OcEKaKX3Eo/sWwSJ7bXbGLDxMf4S\netfY1WDC+4rTqE30JuC++nQviPRdCcZf0AEgM6TxVhYEMVYwV787YO1IH62EBICM\nSkIONOfnusNZ4Skgjq9OzakOOpROZ4tki5cH/5oSDgdcaGPy1CFDpL9fG6er2zzk\nsw3qCbraqZrrlgpinWcAduiao67U/dV18O6OjYzrt33fTKZ0+bXhk1h1gloC21MQ\nya0CXlnfR/FOQhvuK0RlbR3cMfhZQscAEQEAAYkBHwQYAQIACQUCVdSk1wIbDAAK\nCRCTUJ5Lr8ikm8+QB/4uE+AlvFQFh9W8koPdfk7CJF7wdgZZ2NDtktvLL71WuMK8\nPOmf9f5JtcLCX4iJxGzcWogAR5ed20NgUoHUg7jn9Xm3fvP+kiqL6WqPhjazd89h\nk06v9hPE65kp4wb0fQqDrtWfP1lFGuh77rQgISt3Y4QutDl49vXS183JAfGPxFxx\n8FgGcfNwL2LVObvqCA0WLqeIrQVbniBPFGocE3yA/0W9BB/xtolpKfgMMsqGRMeu\n9oIsNxB2oE61OsqjUtGsnKQi8k5CZbhJaql4S89vwS+efK0R+mo+0N55b0XxRlCS\nfaURgAcjarQzJnG0hUps2GNO/+nM7UyyJAGfHlh5\n=EdXO\n-----END PGP PUBLIC KEY BLOCK-----\n"
                ],
                "delete": [
                  "DEADBEEF",
                ]
              }'
        """

        return self.post('/accounts/%s/gpgkeys' % account, **kwargs)

    def delete_gpgkey(self, account, gpgkey, **kwargs):
        """Deletes a GPG key of a user."""

        return self.delete('/accounts/%s/gpgkeys/%s' % (account, gpgkey), **kwargs)

    def list_account_capabilities(self, account, **kwargs):
        """Returns the global capabilities that are enabled for the specified user."""

        return self.get('/accounts/%s/capabilities' % account, params=kwargs)

    def check_account_capabilities(self, account, capability, **kwargs):
        """Checks if a user has a certain global capability."""

        return self.get('/accounts/%s/capabilities/%s' % (account, capability), params=kwargs)

    def list_groups(self, account, **kwargs):
        """Lists all groups that contain the specified user as a member."""

        return self.get('/accounts/%s/groups' % account, params=kwargs)

    def get_avatar(self, account, **kwargs):
        """Retrieves the avatar image of the user."""

        return self.get('/accounts/%s/avatar' % account, params=kwargs)

    def get_avatar_change_url(self, account, **kwargs):
        """Retrieves the URL where the user can change the avatar image."""

        return self.get('/accounts/%s/avatar.change.url' % account, params=kwargs)

    def get_user_preferences(self, account, **kwargs):
        """Retrieves the user’s preferences."""

        return self.get('/accounts/%s/preferences' % account, params=kwargs)

    def set_user_preferences(self, account, **kwargs):
        """Sets the user’s preferences.
        eg.{
            "changes_per_page": 50,
            "show_site_header": true,
            "use_flash_clipboard": true,
            "expand_inline_diffs": true,
            "download_command": "CHECKOUT",
            "date_format": "STD",
            "time_format": "HHMM_12",
            "size_bar_in_change_table": true,
            "review_category_strategy": "NAME",
            "diff_view": "SIDE_BY_SIDE",
            "mute_common_path_prefixes": true,
            "my": [
              {
                "url": "#/dashboard/self",
                "name": "Changes"
              },
              {
                "url": "#/q/has:draft",
                "name": "Draft Comments"
              },
              {
                "url": "#/q/is:watched+is:open",
                "name": "Watched Changes"
              },
              {
                "url": "#/q/is:starred",
                "name": "Starred Changes"
              },
              {
                "url": "#/groups/self",
                "name": "Groups"
              }
            ],
            "change_table": [
              "Subject",
              "Owner"
            ]
          }
        """

        return self.put('/accounts/%s/preferences' % account, **kwargs)

    def get_diff_preferences(self, account, **kwargs):
        """Retrieves the diff preferences of a user."""

        return self.get('/accounts/self/preferences.diff' % account, params=kwargs)

    def set_diff_preferences(self, account, **kwargs):
        """Sets the diff preferences of a user.
        eg.{
            "context": 10,
            "theme": "ECLIPSE",
            "ignore_whitespace": "IGNORE_ALL",
            "intraline_difference": true,
            "line_length": 100,
            "cursor_blink_rate": 500,
            "show_line_endings": true,
            "show_tabs": true,
            "show_whitespace_errors": true,
            "syntax_highlighting": true,
            "tab_size": 8,
            "font_size": 12
          }
        """

        return self.put('/accounts/self/preferences.diff' % account, **kwargs)

    def get_edit_preferences(self, account, **kwargs):
        """Retrieves the edit preferences of a user."""

        return self.get('/accounts/self/preferences.edit' % account, params=kwargs)

    def set_edit_preferences(self, account, **kwargs):
        """Sets the edit preferences of a user.
        eg.{
            "theme": "ECLIPSE",
            "key_map_type": "VIM",
            "tab_size": 4,
            "line_length": 80,
            "indent_unit": 2,
            "cursor_blink_rate": 530,
            "hide_top_menu": true,
            "show_tabs": true,
            "show_whitespace_errors": true,
            "syntax_highlighting": true,
            "hide_line_numbers": true,
            "match_brackets": true,
            "line_wrapping": false,
            "auto_close_brackets": true
          }
        """

        return self.put('/accounts/self/preferences.edit' % account, **kwargs)

    def get_watched_projects(self, account, **kwargs):
        """Retrieves all projects a user is watching."""

        return self.get('/accounts/self/watched.projects' % account, params=kwargs)

    def update_watched_projects(self, account, projects):
        """Add new projects to watch or update existing watched projects.
        Projects that are already watched by a user will be updated with the provided configuration.
        All other projects in the request will be watched using the provided configuration.
        eg. [
                {
                  "project": "Test Project 1",
                  "notify_new_changes": true,
                  "notify_new_patch_sets": true,
                  "notify_all_comments": true,
                }
              ]
        """

        return self.post('/accounts/self/watched.projects' % account, projects)

    def delete_watched_projects(self, account, projects):
        """Projects posted to this endpoint will no longer be watched. The posted body can contain a list of ProjectWatchInfo entities.
            eg. [
                    {
                      "project": "Test Project 1",
                      "filter": "branch:master"
                    }
                  ]
        """

        return self.post('/accounts/self/watched.projects:delete' % account, projects)

    def get_account_external_ids(self, account, **kwargs):
        """Retrieves the external ids of a user account."""

        return self.get('/accounts/%s/external.ids' % account, params=kwargs)

    def delete_account_external_ids(self, account, **kwargs):
        """Delete a list of external ids for a user account.
        The target external ids must be provided as a list in the request body.
        eg.[
            "mailto:john.doe@example.com"
          ]
        """

        return self.post('/accounts/%s/external.ids:delete' % account, **kwargs)

    def list_contributor_agreements(self, account, **kwargs):
        """Gets a list of the user’s signed contributor agreements."""

        return self.get('/accounts/self/agreements' % account, params=kwargs)

    def delete_draft_comments(self, account, **kwargs):
        """Deletes some or all of a user’s draft comments.
            The set of comments to delete is specified as a DeleteDraftCommentsInput entity.
            An empty input entity deletes all comments.
            eg. {
                    "query": "is:abandoned"
                  }
            """

        return self.post('/accounts/%s/drafts.delete' % account, **kwargs)

    def sign_contributor_agreement(self, account, **kwargs):
        """Signs a contributor agreement.
            eg.{
                "name": "Individual"
              }
        """

        return self.put('/accounts/%s/agreements' % account, **kwargs)

    def index_account(self, account, **kwargs):
        """Adds or updates the account in the secondary index."""

        return self.post('/accounts/%s/index' % account, **kwargs)

    def get_changes_with_default_star(self, account, **kwargs):
        """Gets the changes that were starred with the default star by the identified user account.
        This URL endpoint is functionally identical to the changes query GET /changes/?q=is:starred. The result is a list of ChangeInfo entities."""

        return self.get('/accounts/%s/starred.changes' % account, params=kwargs)

    def put_default_star_on_change(self, account, change_id, **kwargs):
        """Star a change with the default label.
        Changes starred with the default label are returned for the search query is:starred or starredby:USER and automatically notify the user whenever updates are made to the change."""

        return self.put('/accounts/%s/starred.changes/%s' % (account, change_id), **kwargs)

    def remove_default_start_from_change(self, account, change_id, **kwargs):
        """Remove the default star label from a change. This stops notifications."""

        return self.delete('/accounts/%s/starred.changes/%s' % (account, change_id), **kwargs)

    def get_starred_changes(self, account, **kwargs):
        """Gets the changes that were starred with any label by the identified user account.
            This URL endpoint is functionally identical to the changes query GET /changes/?q=has:stars.
            The result is a list of ChangeInfo entities."""

        return self.get('/accounts/%s/stars.changes' % account, params=kwargs)

    def get_star_labels_from_change(self, account, change_id, **kwargs):
        """Get star labels from a change."""

        return self.get('/accounts/%s/stars.changes/%s' % (account, change_id),params=kwargs)

    def update_star_labels_on_change(self, account, change_id, **kwargs):
        """
        Update star labels on a change.
        The star labels to be added/removed must be specified in the request body as StarsInput entity.
        Starred changes are returned for the search query has:stars.
        eg. {
                "add": [
                  "blue",
                  "red"
                ],
                "remove": [
                  "yellow"
                ]
              }

        """
        return self.post('/accounts/%s/stars.changes/%s' % (account, change_id), **kwargs)

    def get_version(self):
        """Returns the version of the Gerrit server."""

        return self.get('config/server/version')

    def get_server_info(self):
        """Returns the information about the Gerrit server configuration."""

        return self.get('config/server/info')

    def check_consistency(self, consistency):
        """Runs consistency checks and returns detected problems.
            eg. {
                    "check_accounts": {},
                    "check_account_external_ids": {}
                  }
        """

        return self.post('/config/server/check.consistency', consistency)


    def reload_config(self):
        """Reloads the gerrit.config configuration."""

        return self.post('/config/server/reload', None)

    def confirm_email(self, token):
        """Confirms that the user owns an email address.
            eg. {
                    "token": "Enim+QNbAo6TV8Hur8WwoUypI6apG7qBPvF+bw==$MTAwMDAwNDp0ZXN0QHRlc3QuZGU="
                  }
        """

        return self.put('/config/server/email.confirm', {'token': token})

    def list_caches(self, **kwargs):
        """Lists the caches of the server.
        Caches defined by plugins are included."""

        return self.get('/config/server/caches/', params=kwargs)

    def flush_all_caches(self):

        return self.post('/config/server/caches', {"operation": "FLUSH_ALL"})

    def flush_several_caches_at_once(self, **kwargs):

        data = {"operation": "FLUSH"}
        data.update(kwargs)
        return self.post('/config/server/caches', data)

    def get_cache(self, cache):
        """Retrieves information about a cache."""

        return self.get('/config/server/caches/%s' % cache)

    def flush_cache(self, cache):
        """Flushes a cache."""

        return self.post('/config/server/caches/%s/flush' % cache, None)

    def get_summary(self, **kwargs):
        """Retrieves a summary of the current server state."""

        return self.get('/config/server/summary', params=kwargs)

    def list_capabilities(self):
        """Lists the capabilities that are available in the system. There are two kinds of capabilities: core and plugin-owned capabilities."""

        return self.get('/config/server/capabilities')

    def list_tasks(self):
        """Lists the tasks from the background work queues that the Gerrit daemon is currently performing, or will perform in the near future."""

        return self.get('/config/server/tasks')

    def get_task(self, task):
        """Retrieves a task from the background work queue that the Gerrit daemon is currently performing, or will perform in the near future."""

        return self.get('/config/server/tasks/%s' % task)

    def delete_task(self, task):
        """Kills a task from the background work queue that the Gerrit daemon is currently performing, or will perform in the near future."""

        return self.delete('/config/server/tasks/%s' % task)

    def get_top_menu(self):
        """Returns the list of additional top menu entries."""

        return self.get('/config/server/top-menus')

    def get_default_user_preferences(self):
        """Returns the default user preferences for the server."""

        return self.get('/config/server/preferences')

    def set_default_user_preferences(self, **kwargs):
        """Sets the default user preferences for the server."""

        return self.put('/config/server/preferences', kwargs)

    def get_default_diff_preferences(self):
        """Returns the default diff preferences for the server.."""

        return self.get('/config/server/preferences.diff')

    def set_default_diff_preferences(self, **kwargs):
        """Sets the default diff preferences for the server."""

        return self.put('/config/server/preferences.diff', kwargs)

    def get_default_edit_preferences(self):
        """Returns the default edit preferences for the server.."""

        return self.get('/config/server/preferences.edit')

    def set_default_edit_preferences(self, **kwargs):
        """Sets the default edit preferences for the server."""

        return self.put('/config/server/preferences.edit', kwargs)

    def list_access_rights(self, **kwargs):
        """Lists the access rights for projects.
        The projects for which the access rights should be returned must be specified as project options.
        The project can be specified multiple times."""

        return self.get('/access', params=kwargs)


if __name__ == '__main__':
    gerrit = GerritRestApi('http://172.16.20.56', 'allen.you', 'allen.you')
    # print(gerrit.create_project('vivo4', description='vivo4'))
    # print(gerrit.check_access('oppo', account=1000098, ref='refs/heads/master'))
    # print(gerrit.projects(p='SPF2018'))
    # print(gerrit.groups())
    print(gerrit.get_top_menu())