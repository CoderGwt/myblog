import logging
import json
from datetime import datetime
from urllib.parse import urlencode

from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage

from news.models import Tag, News
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from utils.script import paginator_script
from . import constants

logger = logging.getLogger("django")


def my_dec(func):
    def wrapper(request, *args, **kwargs):
        print("这是装饰器里的内容")
        print("可利用装饰器验证用户登录")
        # if not request.user.is_authenticated:
        #     return render(request, 'users/login.html')
        return func(request, *args, **kwargs)

    return wrapper


class IndexView(View):
    # @my_dec  # 装饰类试图中的函数
    @method_decorator(my_dec)
    def get(self, request):
        return render(request, 'admin/index/index.html')


@method_decorator(my_dec, name='dispatch')
class TagManageView(View):
    # todo 对类/方法使用装饰器，可上方法，可下继承dispatch方法

    # @method_decorator(my_dec)
    # def dispatch(self, request, *args, **kwargs):
    #     return super(TagManageView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        tags = Tag.objects.values('id', 'name').annotate(num_news=Count('news'))\
                    .filter(is_delete=False).order_by('-num_news', '-update_time')
        return render(request, 'admin/news/tags_manager.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(code=Code.PARAMERR, msg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        tag_name = dict_data.get('name')
        if tag_name and tag_name.strip():
            tag_tuple = Tag.objects.filter(is_delete=False).get_or_create(name=tag_name.strip())
            tag_instance, tag_created_boolean = tag_tuple
            new_tag_dict = {
                "id": tag_instance.id,
                "name": tag_instance.name
            }
            return to_json_data(msg="标签创建成功", data=new_tag_dict) if tag_created_boolean else \
                to_json_data(code=Code.DATAEXIST, msg="标签名已存在")
        else:
            return to_json_data(code=Code.PARAMERR, msg="标签名为空")


class TagEditView(View):
    def put(self, request, tag_id):
        json_data = request.body
        if not json_data:
            return to_json_data(code=Code.PARAMERR, msg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        tag_name = dict_data.get('name')
        tag = Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            if tag_name and tag_name.strip():
                if not Tag.objects.only('id').filter(is_delete=False, name=tag_name.strip()).exists():
                    tag.name = tag_name
                    tag.save(update_fields=['name'])
                    return to_json_data(msg="标签更新成功")
                else:
                    return to_json_data(code=Code.DATAEXIST, msg="标签名已存在")
            else:
                return to_json_data(code=Code.PARAMERR, msg="标签名为空")

        else:
            return to_json_data(code=Code.PARAMERR, msg="需要更新的标签不存在")

    def delete(self, request, tag_id):
        tag = Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            # tag.delete()
            tag.is_delete = True
            tag.save(update_fields=['is_delete'])
            return to_json_data(msg="标签更新成功")
        else:
            return to_json_data(code=Code.PARAMERR, msg="需要删除的标签不存在")


class NewsManageView(View):
    """create news manage
    route: /admin/news/
    """

    def get(self, request):
        """
        获取文章列表信息
        """
        tags = Tag.objects.only('id', 'name').filter(is_delete=False)
        newses = News.objects.only('id', 'title', 'author__username', 'tag__name', 'update_time'). \
            select_related('author', 'tag').filter(is_delete=False)

        # 通过时间进行过滤
        try:
            start_time = request.GET.get('start_time', '')
            start_time = datetime.strptime(start_time, '%Y/%m/%d') if start_time else ''

            end_time = request.GET.get('end_time', '')
            end_time = datetime.strptime(end_time, '%Y/%m/%d') if end_time else ''
        except Exception as e:
            logger.info("用户输入的时间有误：\n{}".format(e))
            start_time = end_time = ''

        if start_time and not end_time:
            newses = newses.filter(update_time__lte=start_time)
        if end_time and not start_time:
            newses = newses.filter(update_time__gte=end_time)

        if start_time and end_time:
            newses = newses.filter(update_time__range=(start_time, end_time))

        # 通过title进行过滤
        title = request.GET.get('title', '')
        if title:
            newses = newses.filter(title__icontains=title)

        # 通过作者名进行过滤
        author_name = request.GET.get('author_name', '')
        if author_name:
            newses = newses.filter(author__username__icontains=author_name)

        # 通过标签id进行过滤
        try:
            tag_id = int(request.GET.get('tag_id', 0))
        except Exception as e:
            logger.info("标签错误：\n{}".format(e))
            tag_id = 0
        newses = newses.filter(is_delete=False, tag_id=tag_id) or \
                 newses.filter(is_delete=False)

        # 获取第几页内容
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.info("当前页数错误：\n{}".format(e))
            page = 1
        paginator = Paginator(newses, constants.PER_PAGE_NEWS_COUNT)
        try:
            news_info = paginator.page(page)
        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logging.info("用户访问的页数大于总页数。")
            news_info = paginator.page(paginator.num_pages)

        paginator_data = paginator_script.get_paginator_data(paginator, news_info)

        start_time = start_time.strftime('%Y/%m/%d') if start_time else ''
        end_time = end_time.strftime('%Y/%m/%d') if end_time else ''
        context = {
            'news_info': news_info,
            'tags': tags,
            'paginator': paginator,
            'start_time': start_time,
            "end_time": end_time,
            "title": title,
            "author_name": author_name,
            "tag_id": tag_id,
            "other_param": urlencode({
                "start_time": start_time,
                "end_time": end_time,
                "title": title,
                "author_name": author_name,
                "tag_id": tag_id,
            })
        }
        context.update(paginator_data)
        return render(request, 'admin/news/news_manage.html', context=context)


class NewsEditView(View):
    """
    """
    # permission_required = ('news.change_news', 'news.delete_news')
    # raise_exception = True

    def delete(self, request, news_id):
        """
        删除文章
        """
        news = News.objects.only('id').filter(id=news_id).first()
        if news:
            news.is_delete = True
            news.save(update_fields=['is_delete'])
            return to_json_data(msg="文章删除成功")
        else:
            return to_json_data(code=Code.PARAMERR, msg="需要删除的文章不存在")

    def put(self, request):
        pass


class NewsPubView(View):
    """文章发布编辑view
    /news/pub/
    """
    # permission_required = ('news.add_news', 'news.view_news')
    # raise_exception = True

    def get(self, request):
        """
        获取文章标签
        """
        tags = Tag.objects.only('id', 'name').filter(is_delete=False)

        return render(request, 'admin/news/news_pub.html', locals())