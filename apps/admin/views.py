from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count


from news.models import Tag
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map

def my_dec(func):
    def wrapper(self, request, *args, **kwargs):
        print("这是装饰器里的内容")
        print("可利用装饰器验证用户登录")
        if not request.user.is_authenticated:
            return render(request, 'users/login.html')
        return func(self, request, *args, **kwargs)

    return wrapper


class IndexView(View):
    @my_dec  # 装饰类试图中的函数
    def get(self, request):
        return render(request, 'admin/index/index.html')


class TagManageView(View):
    def get(self, request):
        tags = Tag.objects.values('id', 'name').annotate(num_news=Count('news'))\
                    .filter(is_delete=False).order_by('-num_news', '-update_time')
        return render(request, 'admin/news/tags_manager.html', locals())

    def post(self, request):
        pass

    def put(self, request, tag_id):
        pass

    def delete(self, request, tag_id):
        tag = Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            # tag.delete()
            tag.is_delete = True
            tag.save(update_fields=['is_delete'])
            return to_json_data(msg="标签更新成功")
        else:
            return to_json_data(code=Code.PARAMERR, msg="需要删除的标签不存在")
