from django.views import View
from django.shortcuts import render

# Create your views here.


class IndexView(View):
    def get(self, request):
        return render(request, 'course/course(1).html')