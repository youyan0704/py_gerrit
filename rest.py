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

    def ls_groups(self, **kwargs):
        """
            列出组别
        """
        groups = self.get('groups', params=kwargs)

        return groups

    def rename_group(self, group_owner_id, new_name):
        """
            重命名组别
        """
        response = self.put('groups/%s/name' % group_owner_id, data={'name': new_name})
        # return _decode_response(response)

    def group_detail(self, group_id):
        """
            组别详尽信息
        """
        group = self.get('groups/%s/detail' % group_id)

        return group

    def ls_members(self, group):
        """
            列出组别成员
        """
        members = self.get('groups/%s/members' % group)
        return members

    def ls_groups_in_group(self, group):
        """
            组别中包含的组
        """
        groups = self.get('groups/%s/groups' % group)
        return groups

    def ls_plugins(self,):
        """
            列出插件
        """
        plugins = self.get('plugins', params={'all': '', 'n': n, 'S': s})
        return plugins


if __name__ == '__main__':
    gerrit = GerritRestApi('http://172.16.20.56', 'allen.you', 'allen.you')
    # print(gerrit.create_project('vivo4', description='vivo4'))
    # print(gerrit.check_access('oppo', account=1000098, ref='refs/heads/master'))
    # print(gerrit.projects(p='SPF2018'))
    print(gerrit.branches('vivo3', n=1))
