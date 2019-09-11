from django.views import View
from django.http import HttpResponse
from django.shortcuts import render

from .models import Tag


class IndexView(View):
    def get(self, request):
        # todo 使用only进行select查询你，优化查询效率
        tags = Tag.objects.only('id', 'name').filter(is_delete=False).all()
        return render(request, 'news/index.html', locals())


class SearchView(View):
    def get(self, request):
        return render(request, 'news/search.html')