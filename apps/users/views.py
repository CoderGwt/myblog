import json

from django.views import View
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout

from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from .forms import RegisterForm, LoginForm
from users.models import Users


class LoginView(View):
    """
    user login
    /user/login/
    """
    def get(self, request):
        return render(request, 'users/login.html')\


    def post(self, request):
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(code=Code.PARAMERR, msg="缺少参数")
            dict_data = json.loads(json_data.decode("utf-8"))
        except (Exception, ) as e:
            return to_json_data(code=Code.UNKOWNERR, msg="未知错误")

        forms = LoginForm(data=dict_data, request=request)
        if forms.is_valid():
            # 校验成功，直接返回数据
            return to_json_data(code=Code.OK, msg='登录成功')
        else:
            error_list = []
            for item in forms.errors.get_json_data().values():
                error_list.append(item[0].get("message"))

            err_msg = "/".join(error_list)
            return to_json_data(code=Code.PARAMERR, msg=err_msg)


class LogoutView(View):
    """
    退出登录功能
    """
    def get(self, request):
        logout(request)
        # 重定向到首页/登录界面
        return redirect(reverse('news:index'))


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

            # 6. 将用户信息保存到数据库  记得是create_user, 而不是 create
            user = Users.objects.create_user(username=username, password=password, mobile=mobile)
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

