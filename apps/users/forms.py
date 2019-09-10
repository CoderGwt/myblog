"""
用户注册form验证
用户名 / 密码，验证密码/ 手机号码 / 短信验证码 /
"""
import re

from django import forms
from django.db.models import Q
from django_redis import get_redis_connection
from django.contrib.auth import login

from verifications.constants import SMS_CODE_NUMS
from users.models import Users
from . import constants


class RegisterForm(forms.Form):
    username = forms.CharField(
        label="用户名",
        max_length=12, min_length=5,
        error_messages={"required": "用户名不能为空 form",
                        'min_length': "用户名长度要大于5位 from",
                        'max_length': "用户名长度要小于20 form"}
    )

    password = forms.CharField(
        label="密码",
        max_length=20, min_length=6,
        error_messages={
            "required": '密码不能为空 form',
            'min_length': "密码长度要大于6 form",
            'max_length': "密码长度要小于20 form"}
    )

    password_repeat = forms.CharField(
        label="确认密码",
        max_length=20, min_length=6,
        error_messages={
            'required': '密码不能为空 form',
            'min_length': "密码长度要大于6 form",
            'max_length': "密码长度要小于20 form",
        }
    )

    mobile = forms.CharField(
        label='手机号码',
        max_length=11, min_length=11,
        error_messages={
            'required': "手机号不能为空 form",
            'min_length': '请输入11位数的手机号码 form',
            'max_length': "请输入11位数的手机号码 form"
        }
    )

    sms_code = forms.CharField(
        label="短信验证码",
        max_length=SMS_CODE_NUMS, min_length=SMS_CODE_NUMS,
        error_messages={
            'required': '短信验证码不能为空 form',
            'min_length': "短信验证码长度有误 form",
            'max_length': "短信验证码长度有误 form"
        }
    )

    def clean_mobile(self):
        """
        校验手机号
        :return: 手机号
        """
        # 1. 取出手机号
        tel = self.cleaned_data.get("mobile")
        # 2. 正则匹配验证手机号格式
        if not re.match("^1[3-9]\d{9}$", tel):
            raise forms.ValidationError("手机号格式有误 raise")

        # 3. 检查手机号是否被注册
        if Users.objects.filter(mobile=tel).exists():
            raise forms.ValidationError("手机号已注册，请重新输入 raise")

        return tel

    def clean(self):
        """
        1. 检验两次密码输入是否一致
        2. 校验验证码输入是否正确
        :return:
        """
        # 获取参数
        clean_data = super().clean()
        password = clean_data.get('password')
        password_repeat = clean_data.get("password_repeat")
        mobile = clean_data.get("mobile")
        sms_code = clean_data.get("sms_code")

        # 判断两次密码输入是否一致
        if password != password_repeat:
            raise forms.ValidationError("两次密码输入不一致，请重新输入")

        # 建立redis连接，取出保存的短信验证码，判断是否与用户输入的一致
        conn_redis = get_redis_connection(alias="verify_codes")
        # sms_key 可encode("utf-8") ，也可以不用，自动转，亲测有效
        sms_key = "sms_{}".format(mobile)
        real_sms_code = conn_redis.get(sms_key)

        if not real_sms_code or sms_code != real_sms_code.decode("utf-8"):
            raise forms.ValidationError("短信验证码输入错误，请重新输入")


class LoginForm(forms.Form):
    user_account = forms.CharField(label="用户账号-手机/用户名")
    password = forms.CharField(
        label="密码", min_length=6, max_length=20,
        error_messages={
            'required': "密码不能为空 form",
            'min_length': '密码长度须大于6位',
            'max_length': "密码长度须小于20位"
        }
    )
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        # todo 需要super()调用父类的init
        # todo 上面使用get获取request对象的时候，这一步会报错。使用pop就不会，咋回事？？？
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_user_account(self):
        user_info = self.cleaned_data.get("user_account")

        if not re.match("^1[3-9]\d{9}$", user_info) and (len(user_info) < 5 or len(user_info) > 20):
            raise forms.ValidationError("用户账号格式有误")

        return user_info

    def clean(self):
        clean_data = super().clean()
        # 获取参数
        user_info = clean_data.get('user_account')
        password = clean_data.get("password")
        remember = clean_data.get("remember_me")

        # 查询数据库，是否存在手机号或用户名为user_info的，使用Q变量 和 |
        user_query = Users.objects.filter(Q(mobile=user_info) | Q(username=user_info))
        if user_query:
            user = user_query.first()
            # 验证用户密码是否正确
            if user.check_password(password):
                # 判断是否有记住会话功能，记住5天
                if remember:
                    self.request.session.set_expiry(constants.USER_SESSION_EXPIRED)
                else:
                    # 没有记住，浏览器关闭即过时
                    self.request.session.set_expiry(0)

                # todo 登录
                login(request=self.request, user=user)
            else:
                raise forms.ValidationError("密码输入错误，请重新输入！")
        else:
            raise forms.ValidationError("用户不存在，请重新输入 raise")


