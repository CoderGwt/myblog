import logging

from django.views import View
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage

from . import constants
from .models import Tag, News
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map


class IndexView(View):
    """首页标签数据
    /index/
    """
    def get(self, request):
        # todo 使用only进行select查询你，优化查询效率
        tags = Tag.objects.only('id', 'name').filter(is_delete=False).all()
        return render(request, 'news/index.html', locals())


class NewsView(View):
    """新闻数据
    /news/
    1. 创建类视图
    """
    def get(self, request):
        # 2. 获取参数并校验参数
        try:
            tag_id = int(request.GET.get("tag_id", 0))
        except (Exception, ) as e:
            tag_id = 0
        try:
            page = int(request.GET.get("page", 1))
        except (Exception, ) as e:
            page = 1
        # 3. 查询数据
        news_query = News.objects.select_related('tag', 'author').\
            only('title', 'digest', 'image_url', 'update_time', 'tag__name', 'author__username')

        news = news_query.filter(is_delete=False, tag_id=tag_id) or news_query.filter(is_delete=False)

        paginator = Paginator(news, constants.PER_PAGE_NEWS_COUNT)
        try:
            news_info = paginator.page(page)
        except EmptyPage:
            # 若用户访问的页数超过最大，就返回最后一页的数据
            news_info = paginator.page(paginator.num_pages)

        # 4. 序列化数据
        news_info_list = []
        for item in news_info:
            news_info_list.append({
                'title': item.title,
                'digest': item.digest,
                'image_url': item.image_url,
                'tag_name': item.tag.name,
                'author': item.author.username,
                'update_time': item.update_time.strftime("%Y年%m月%d日 %H:%M")  # 格式化时间
            })

        # 5. 返回给前端
        data = {
            'news': news_info_list,
            'total_pages': paginator.num_pages
        }
        return to_json_data(data=data)


class SearchView(View):
    def get(self, request):
        return render(request, 'news/search.html')