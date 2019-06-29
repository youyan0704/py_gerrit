# -*- coding: utf-8 -*-
# @Time    : 19-5-8 下午4:10
# @Author  : allen.you


base_command = 'ssh %s gerrit %s'
DEFAULT_PORT = 29418

GERRIT_MAGIC_JSON_PREFIX = ")]}\'\n"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    # 'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Cookie': 'GERRIT_UI=GWT'}
