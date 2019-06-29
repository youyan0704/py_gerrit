# -*- coding: utf-8 -*-
# @Time    : 19-5-21 下午6:14
# @Author  : allen.you
from py_gerrit.models import User
from py_gerrit.utils.jsonModel import jsonModel


@jsonModel()
class Option(object):
    def __init__(self):
        pass


@jsonModel(objectMap={'options': Option})
class Group(object):
    def __init__(self):
        self.id = ''
        self.group_id = 0
        self.name = ''
        self.owner = ''
        self.owner_id = ''
        self.url = ''
        self.options = {}
        self.created_on = ''
        self.description = ''

    def __repr__(self):
        return 'Group Owner: %s' % self.owner + (', description: %s' if self.description else ', created_on: %s' % self.created_on)


@jsonModel(objectMap={'options': Option}, listClassMap={'members': User, 'includes': Group})
class GroupDetail(object):
    def __init__(self):
        self.id = ''
        self.group_id = 0
        self.name = ''
        self.owner = ''
        self.owner_id = ''
        self.url = ''
        self.options = {}
        self.created_on = ''
        self.description = ''
        # 组员
        self.members = []
        # 包含组
        self.includes = []

    def __repr__(self):
        return 'Group Owner: %s, members: %s, includes: %s' % (self.owner, self.members, self.includes)