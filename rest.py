# -*- coding: utf-8 -*-
# @Time    : 19-5-9 上午11:27
# @Author  : allen.you
import logging

import requests
from requests.auth import HTTPBasicAuth
from .models.plugin import Plugin
from .models.group import Group
from .models.user import User
from .models.project import Project
from .utils.util import _decode_response, decode_model

log = logging.getLogger(__name__)


class GerritRestApi(object):

    def __init__(self, url, username, password, verify=True):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Cookie': 'GERRIT_UI=GWT;'}
        self.kwargs = {'auth': HTTPBasicAuth(username, password),
                       'verify': verify,
                       'headers': headers}
        self.url = url.rstrip('/')

        if not self.url.endswith('/'):
            self.url += '/'

        self.session = requests.Session()
        self._login()
        logging.debug("url %s", self.url)

    def make_url(self, endpoint):
        endpoint = endpoint.lstrip('/')
        return self.url + endpoint + '/'

    def _login(self, **kwargs):
        kwargs.update(self.kwargs.copy())
        self.session.get(self.make_url('login'), **kwargs)
        self.kwargs['headers'].update({
            'Cookie': ';'.join('='.join([key, value]) for key, value in self.session.cookies.items())
        })

    def get(self, endpoint, **kwargs):
        kwargs.update(self.kwargs.copy())
        response = self.session.get(self.make_url(endpoint), **kwargs)
        return _decode_response(response)

    def put(self, endpoint, data, **kwargs):
        kwargs.update(self.kwargs.copy())
        kwargs["headers"].update(
            {"Content-Type": "application/json;charset=utf-8"})
        response = self.session.put(self.make_url('a/' + endpoint), data, **kwargs)
        print(response.status_code, response.text)
        print(self.kwargs)
        return _decode_response(response)

    def post(self, endpoint, data, **kwargs):
        kwargs.update(self.kwargs.copy())
        kwargs["headers"].update(
            {"Content-Type": "application/json;charset=utf-8"})
        response = self.session.post(self.make_url(endpoint), data, **kwargs)
        print(self.kwargs)
        print(response)
        if response.text is None:
            return response
        return _decode_response(response)

    def delete(self, endpoint, **kwargs):
        kwargs.update(self.kwargs.copy())
        response = self.session.delete(self.make_url(endpoint), **kwargs)
        return _decode_response(response)

    def ls_projects(self):
        projects = self.get('projects')
        return decode_model(projects, Project)

    def create_project(self, project, parent='All-Projects'):
        project = self.put('projects/%s' % project, data={'create_empty_commit': True,
                                           'name': project,
                                           'parent': parent})

        return decode_model(project, Project)


    def delete_project(self, project, force=False, preserve=False):
        """
            此方法需要安装delete-project 插件，
        """
        try:
            response = self.post('projects/%s/delete-project~delete' % project, {'force': 'true' if force else 'false',
                                                                                 'preserve': 'true' if preserve else 'false'})
            if 200 <= response.status_code < 300:
                logging.info('delete %s sccessfully' % project)
        except:
            logging.info('delete %s failed' % project)

    def create_branch(self, project, branch, revision='refs/meta/config'):
        pass

    def delete_branch(self, project, branch):
        pass

    def ls_groups(self):
        groups = self.get('groups')
        return decode_model(groups, Group)

    def rename_group(self, group_owner_id, new_name):
        response = self.put('groups/%s/name' % group_owner_id, {'name': new_name})
        print(response)
        # return _decode_response(response)

    def ls_members(self, group_id):
        all_members, all_includes = [], []
        members = self.get('groups/%s/detail' % group_id)
        for member in members['members']:
            user = User()
            user.fromJson(member)
            all_members.append(user)

        for include in members['includes']:
            group = Group()
            group.fromJson(include)
            all_includes.append(group)

        return all_members, all_includes

    def ls_plugins(self):
        plugins = self.get('plugins')
        return decode_model(plugins, Plugin)


if __name__ == '__main__':
    gerrit = GerritRestApi('http://172.16.20.56', 'allen.you', 'allen.you')
    # gerrit.ls_projects()
    # gerrit.rename_group('61e7059a35bb3c4a8d5925da25dd4f973fbac095', 'scm2')
    # gerrit.delete_project('tester')
    gerrit.create_project('vivo')