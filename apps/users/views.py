import json

from django.views import View
from django.shortcuts import render
from django.contrib.auth import login

from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from .forms import RegisterForm
from users.models import Users


class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')


class RegisterView(View):
    """ 1. 创建一个类
    user register
    /user/register/
    """
    # 2. 创建get方法
    def get(self, request):
        return render(request, 'users/register.html')

    # 3. 创建post方法
    def post(self, request):
        # 4. 获取前端传过来的参数
        json_data = request.body
        if not json_data:
            return to_json_data(code=Code.PARAMERR, msg="缺少参数，请重新输入")
        dict_data = json.loads(json_data.decode("utf-8"))
        # 5. 校验参数 [form表单校验]
        form = RegisterForm(data=dict_data)
        if form.is_valid():
            data = form.cleaned_data
            username = data.get("username")
            password = data.get('password')
            mobile = data.get('mobile')

            # 6. 将用户信息保存到数据库
            user = Users.objects.create(username=username, password=password, mobile=mobile)
            # 登录，保存session等信息
            login(request, user)

            # 7. 将结果返回给前端
            return to_json_data(code=Code.OK, msg="注册成功")
        else:
            # 返回错误信息列表
            err_list = []
            for item in form.errors.get_json_data().values():
                err_list.append(item[0].get("message"))
            err_msg_str = "/".join(err_list)
            return to_json_data(code=Code.PARAMERR, msg=err_msg_str)

