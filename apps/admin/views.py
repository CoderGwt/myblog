import json

from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
from django.utils.decorators import method_decorator


from news.models import Tag
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map


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


class TagManageView(View):
    def get(self, request):
        tags = Tag.objects.values('id', 'name').annotate(num_news=Count('news'))\
                    .filter(is_delete=False).order_by('-num_news', '-update_time')
        return render(request, 'admin/news/tags_manager.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
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

    def put(self, request, tag_id):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
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
