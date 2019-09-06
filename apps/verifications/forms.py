from django import forms
from django.core.validators import RegexValidator

from users.models import Users
from django_redis import get_redis_connection


mobile_validator = RegexValidator(r'^1[3-9]\d{9}$', '手机号格式不正确')


class CheckImageCodeForm(forms.Form):
    """
    check sms code
    """
    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validator, ],
                             error_messages={
                                 'min_length': "手机号长度有误",
                                 'max_length': "手机号长度有误",
                                 'required': "手机号不能为空"
                             })
    image_code_id = forms.UUIDField(error_messages={"required": "图片UUID不能为空"})
    text = forms.CharField(max_length=4, min_length=4,
                           error_messages={
                               "min_length": "图片验证码长度有误",
                               "max_length": "图片验证码长度有误",
                               "required": "图片验证码不能为空"
                           })

    def clean_mobile(self):  # todo 固定格式 clean_...(self)....
        tel = self.cleaned_data.get('mobile')
        if Users.objects.filter(mobile=tel).count():
            raise forms.ValidationError("手机号已注册，请重新输入(raise)")
        return tel

    def clean(self):
        cleaned_data = super().clean()
        mobile_num = cleaned_data.get("mobile")
        image_uuid = cleaned_data.get("image_code_id")
        image_text = cleaned_data.get("text")

        # 1. 获取验证码
        con_redis = get_redis_connection(alias="verify_codes")  # 创建链接
        # 记得encode，也可以real_image_code decode 但是有一个问题，如果不存在的话，需要先做判断，多了一步
        img_key = "img_{}".format(image_uuid).encode("utf-8")

        real_image_code = con_redis.get(img_key)
        # todo 取出来之后，需要做删除操作，不然5分钟内，可以反复无限次的操作验证码
        con_redis.delete(img_key)

        # 2. 判断用户输入的验证码是否正确
        if not real_image_code or image_text.upper() != real_image_code.decode('utf8').upper():
            raise forms.ValidationError("图片验证码验证失败（raise）")

        # 3. 判断在60秒之内是否有发送短信的记录
        sms_flag_fmt = "sms_flag_{}".format(mobile_num).encode("utf-8")  # key
        sms_flag = con_redis.get(sms_flag_fmt)  # 是否有value值
        if sms_flag:
            raise forms.ValidationError("获取短信验证码过于频繁（raise）")



