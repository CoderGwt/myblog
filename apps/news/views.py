import logging
import json

from django.views import View
from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage

from . import constants
from .models import Tag, News, Banner, HotNews, Comment
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map


class IndexView(View):
    """首页标签数据
    /index/
    """
    def get(self, request):
        # todo 使用only进行select查询你，优化查询效率
        tags = Tag.objects.only('id', 'name').filter(is_delete=False).all()
        hot_news = HotNews.objects.select_related('news') \
            .only('news__title', 'news__image_url', 'news_id').filter(is_delete=False) \
            .order_by('priority', '-news__clicks', '-update_time')[:constants.SHOW_HOT_NEWS_COUNT]
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
                'id': item.id,
                'title': item.title,
                'digest': item.digest,
                'image_url': item.image_url,
                'tag_name': item.tag.name,
                'author': item.author.username if item.author else "",
                'update_time': item.update_time.strftime("%Y年%m月%d日 %H:%M")  # 格式化时间
            })

        # 5. 返回给前端
        data = {
            'news': news_info_list,
            'total_pages': paginator.num_pages
        }
        return to_json_data(data=data)


class NewsDetailView(View):
    """
    news detail view
    /news/<int:news_id>
    """
    def get(self, request, news_id):
        new = News.objects.select_related('author', 'tag').\
            only('tag__name', 'author__username', 'title', 'content', 'update_time').\
            filter(is_delete=False, id=news_id).first()
        if not new:
            raise Http404("<新闻{}>不存在".format(news_id))
            # return HttpResponseNotFound("<h1>NOT FOUND</h1>")  # 返回404， NOT FOUND

        comments_list = []
        comments = Comment.objects.select_related('author', 'parent').\
            only('content', 'author__username', 'update_time',
                 'parent__author__username', 'parent__content', 'parent__update_time').\
            filter(is_delete=False, news_id=news_id)

        for comment in comments:
            comments_list.append(comment.to_json_data())

        return render(request, 'news/news_detail.html', locals())


class BannerView(View):
    """
    create get banner view
    /news/banners/
    """
    def get(self, request):
        banners = Banner.objects.select_related('news').only('image_url', 'news_id', 'news__title')\
            .filter(is_delete=False)[:constants.SHOW_BANNER_COUNT]  # 只取出六条
        banner_list = []
        for banner in banners:
            banner_list.append({
                'image_url': banner.image_url,
                'title': banner.news.title,
                'news_id': banner.news_id
            })

        # 返回数据给前端
        data = {
            'banners': banner_list
        }
        return to_json_data(data=data)


class NewsCommentView(View):
    """
    create news comment
    /news/<int:news_id>/comments/
    """
    def post(self, request, news_id):
        # 判断用户是否登录 使用 request.user.is_authenticated
        if not request.user.is_authenticated:

            return to_json_data(code=Code.SESSIONERR, msg=error_map[Code.SESSIONERR])

        try:
            json_data = request.body
            if not json_data:
                return to_json_data(code=Code.PARAMERR, msg="参数为空，请重新输入")
            dict_data = json.loads(json_data.decode("utf-8"))
        except (Exception, ) as e:
            return to_json_data(code=Code.UNKOWNERR, msg=error_map[Code.UNKOWNERR])

        content = dict_data.get('content')
        if not content:
            return to_json_data(code=Code.PARAMERR, msg='评论内容不能为空')
        parent_id = dict_data.get("parent_id")

        if parent_id:
            try:
                parent_id = int(parent_id)

                # 判断news_id 和 parent_id 数据是否存在
                if not Comment.objects.only('id').filter(is_delete=False, id=parent_id, news_id=news_id).exists():
                    return to_json_data(code=Code.PARAMERR, msg=error_map[Code.PARAMERR])
            except (Exception, ) as e:
                return to_json_data(code=Code.PARAMERR, msg="未知错误")
        news_comment = Comment()
        news_comment.news_id = news_id
        news_comment.content = content
        # 存在 或者 None 或者 “” 所以还是要判断
        news_comment.parent_id = parent_id if parent_id else None
        news_comment.author_id = request.user.id
        news_comment.save()

        return to_json_data(data=news_comment.to_json_data())


class SearchView(View):
    def get(self, request):
        return render(request, 'news/search.html')