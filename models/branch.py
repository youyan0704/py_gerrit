# -*- coding: utf-8 -*-
# @Time    : 19-6-25 下午5:09
# @Author  : allen.you

from py_gerrit.utils.jsonModel import jsonModel
from .project import Weblink


@jsonModel(listClassMap={'web_links': Weblink})
class Branch(object):
    def __init__(self):
        self.ref = ''
        self.revision = ''
        self.web_links = []


    def __repr__(self):
        return 'Branch: %s, revision: %s' % (self.ref, self.revision)