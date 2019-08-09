from django.http import JsonResponse

from .res_code import Code


def to_json_data(code=Code.OK, msg='', data=None, **kwargs):
    """
    封装json返回数据格式
    :param code: code
    :param msg: msg
    :param data: data
    :param kwargs:
    :return: json_dict
    """
    json_dict = {'code': code, 'msg': msg, 'data': data}

    if kwargs:
        json_dict.update(kwargs)

    return JsonResponse(data=json_dict)