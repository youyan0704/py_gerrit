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

    def get(self, endpoint, **kwargs):
        kwargs.update(self.kwargs.copy())
        print(kwargs)
        response = self.session.get(self.make_url(endpoint), **kwargs)
        return _decode_response(response)

    def put(self, endpoint, data, **kwargs):
        kwargs.update(self.kwargs.copy())
        if self.session.cookies.get('XSRF_TOKEN'):
            kwargs["headers"].update(
                {"x-gerrit-auth": self.session.cookies.get('XSRF_TOKEN')})
        print(kwargs)
        print(self.session.cookies)
        response = self.session.put(self.make_url('a/' + endpoint), data, **kwargs)
        return _decode_response(response)

    def post(self, endpoint, data, **kwargs):
        kwargs.update(self.kwargs.copy())
        kwargs["headers"].update(
            {"Content-Type": "application/json;charset=utf-8"})
        print(kwargs)
        print(self.session.cookies)
        response = self.session.post(self.make_url(endpoint), data, **kwargs)
        return _decode_response(response)

    def delete(self, endpoint, **kwargs):
        kwargs.update(self.kwargs.copy())
        response = self.session.delete(self.make_url(endpoint), **kwargs)
        return _decode_response(response)


class GerritRestApi(ResetApi):

    def __init__(self, url, username, password):
        super().__init__(url, username, password)
        self._login()

    def _login(self):
        self.get('login')
        self.kwargs['headers'].update({
            'Cookie': self.kwargs['headers']['Cookie'] + '; ' + '; '.join('='.join([key, value]) for key, value in self.session.cookies.items())
        })

        self.kwargs.pop('auth')

    def ls_projects(self, n=None, s=None, query='state:active OR state:read-only'):
        """
            列出项目
        """
        projects = self.get('projects', params={'n': n, 'S': s, 'query': query})

        return projects

    def project_config(self, project):
        """
            项目配置信息
        """
        config = self.get('projects/%s/config' % project)

        return config


    def project_access(self, project):
        """
            项目权限信息
        """

        access = self.get('access', params={'project': project})

        return access

    def create_project(self, project, parent='All-Projects', create_empty_commit=True, permissions_only=False):
        """
            创建项目
        """
        return self.put('projects/%s' % project, data={'name': project,
                                                       'parent': parent,
                                                       'create_empty_commit': create_empty_commit,
                                                       'permissions_only': permissions_only,
                                                       })

    def delete_project(self, project, force=False, preserve=False):
        """
            删除项目, 此方法需要安装delete-project 插件，
        """

        return self.post('projects/%s/delete-project~delete' % project, data={'force': 'true' if force else 'false',
                                                                              'preserve': 'true' if preserve else 'false'})

    def ls_branches(self, project, n=None, s=None):
        """
            项目的分支
        """
        branches = self.get('projects/%s/branches' % project, params={'n': n, 'S': s})

        return branches

    def create_branch(self, project, branch, revision='master'):
        """
            创建项目的分支
        """
        return self.put('projects/%s/branches/%s' % (project, branch), data={'revision': revision})

    def delete_branch(self, project, branch):
        """
            删除项目分支
        """
        return self.delete('projects/%s/branches/%s' % (project, branch))

    def ls_groups(self, n=None, s=None):
        """
            列出组别
        """
        groups = self.get('groups', params={'n': n, 'S': s})

        return groups

    def rename_group(self, group_owner_id, new_name):
        """
            重命名组别
        """
        response = self.put('groups/%s/name' % group_owner_id, data={'name': new_name})
        print(response)
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

    def ls_plugins(self, n=None, s=None):
        """
            列出插件
        """
        plugins = self.get('plugins', params={'all': '', 'n': n, 'S': s})
        return plugins


if __name__ == '__main__':
    gerrit = GerritRestApi('http://172.16.20.56', 'allen.you', 'allen.you')
    gerrit.ls_plugins()
    # gerrit.create_project('huawei')