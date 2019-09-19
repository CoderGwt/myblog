import logging

from django.views import View
from django.shortcuts import render
from django.http import FileResponse, Http404
import requests
from django.utils.encoding import escape_uri_path

from .models import Doc
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from myblog.settings import BASE_DIR

logger = logging.getLogger('django')


class IndexView(View):
    def get(self, request):
        """
        get docs msg
        :param request:
        :return:
        """
        docs = Doc.objects.defer('create_time', 'update_time', 'author').filter(is_delete=False).all()
        return render(request, 'doc/docDownload.html', locals())


class DownloadDocView(View):
    """
    create download doc view
    route: /docs/<int:doc_id>/
    """
    def get(self, request, doc_id):
        doc = Doc.objects.only('file_url').filter(is_delete=False, id=doc_id).first()
        if not doc:
            raise Http404("文档不存在")

        doc_url = doc.file_url
        doc_url = BASE_DIR + doc_url
        try:
            # todo 如果是请求第三方的文件，就需要使用requets.get(url) 请求数据，如下
            # res = FileResponse(requests.get(doc_url), stream=True)  # 加上stream参数，使其不一次性下载全部
            # todo FileResponse 接收的是一个文件对象，这里直接打开文件
            res = FileResponse(open(doc_url, 'rb'))
        except (Exception, ) as e:
            logging.error("获取文档出现异常, {}".format(e))
            raise Http404('文档下载异常')

        ex_name = doc_url.split(".")[-1]
        if not ex_name:
            raise Http404("文档url异常")
        else:
            ex_name = ex_name.lower()

        # todo 判断文件的类型，设置对应的Content-type
        if ex_name == "pdf":
            res["Content-type"] = "application/pdf"
        elif ex_name == "zip":
            res["Content-type"] = "application/zip"
        elif ex_name == "doc":
            res["Content-type"] = "application/msword"
        elif ex_name == "xls":
            res["Content-type"] = "application/vnd.ms-excel"
        elif ex_name == "docx":
            res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ex_name == "ppt":
            res["Content-type"] = "application/vnd.ms-powerpoint"
        elif ex_name == "pptx":
            res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

        else:
            raise Http404("文档格式不正确！")

        # todo 通过escape_uri_path 解析获取到文件名称 【之前导出excel也用到了这个】，不然会在网页直接打开文件

        doc_filename = escape_uri_path(path=doc_url.split('/')[-1])
        # attachment  设置为inline，会直接打开
        # *=UTF-8 也是必须的，设置下载的文件名，不然会以默认的”下载“
        res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_filename)
        return res
