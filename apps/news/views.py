from django.views import View
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


class IndexView(View):
    def get(self, request):
        return render(request, 'news/index.html')


class SearchView(View):
    def get(self, request):
        return render(request, 'news/search.html')