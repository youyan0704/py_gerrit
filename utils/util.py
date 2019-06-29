# -*- coding: utf-8 -*-
# @Time    : 19-5-21 下午5:02
# @Author  : allen.you
import json

from py_gerrit.config import GERRIT_MAGIC_JSON_PREFIX


def _decode_response(response):
    content = response.text.strip()
    response.raise_for_status()
    if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
        content = content[len(GERRIT_MAGIC_JSON_PREFIX):]
        return json.loads(content)
    else:
        return response.status_code


def decode_model(json_obj, object):

    if json_obj is None:
        return None

    obj = object()
    obj.fromJson(json_obj)

    return obj


def decode_model_from_list(json_obj_list, object):
    all_objects = []

    if json_obj_list is None:
        return None

    for json_obj in json_obj_list:
        obj = decode_model(json_obj, object)
        all_objects.append(obj)

    return all_objects


def decode_model_from_json(json_obj, object):
    all_objects = []

    if json_obj is None:
        return None

    for key, value in json_obj.items():
        obj = decode_model(value, object)
        all_objects.append(obj)

    return all_objects
