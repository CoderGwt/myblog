import logging
import json
import string
import random

from django.http import JsonResponse
from django_redis import get_redis_connection
from django.views import View
from django.http import HttpResponse

from . import constants
from utils.captcha.captcha import captcha
from utils.json_fun import to_json_data
from utils.res_code import error_map, Code
from users.models import Users
from .forms import CheckImageCodeForm
from utils.yuntongxun.sms import CCP

# Create your views here.

# 导入日志器
logger = logging.getLogger("blog")


class ImageCode(View):
    # 1. todo 创建一个公共类
    """
        define image verification view
        /image_code/<uuid:image_code_id>/
        """
    # 步骤：
    # 2. todo 从前端获取到参数并做验证
    def get(self, request, image_code_id):
        # 3. todo 生成验证码文本和验证码图片
        text, image = captcha.generate_captcha()  # 直接调用，返回文本和图片

        # 4. todo 建立redis连接, 将图片验证码保存到redis 【访问速度快】  key-value 键值对形式nozhogndulezhgezhendehansonanshoukaigemao
        con_redis = get_redis_connection(alias='verify_codes')  # todo 在settings中配置redis的别名
        img_key = "img_{}".format(image_code_id)  # 构建出键值对的key 的形式
        con_redis.setex(img_key, constants.IMAGE_CODE_REDIS_EXPIRES, text)  # todo 通过con_redis.setex 设置key-time-value

        # 打印日志
        logger.info("image_code: {}".format(text))

        # 5. todo 把验证码图片返回给前端 [HttpResponse]
        return HttpResponse(content=image, content_type='image/jpg')  # 传输图片的时候，接收的是二进制，需要指定content_type为image/jpg 为图片类型


class CheckUsernameView(View):
    # 1. 创建一个类
    """
        check username if exists
        /username/(?P<username>\w{5,20})/
        """
    # 2. 校验参数
    def get(self, request, username):
        user = Users.objects.filter(username=username)
        # 3. 查询数据
        if not user:
            data = {
                "username": username,
                'msg': "用户名可用",
                'count': user.count()
            }
        else:
            data = {
                'username': username,
                'msg': '用户名已注册，请重新输入',
                'count': user.count()
            }
        # 4. 返回的结果
        # return JsonResponse(data=data)
        return to_json_data(data=data)


class CheckMobileView(View):
    # 1. 创建一个类
    """
        check if mobile exists
        /mobiles/(?P<mobile>1[3-9]\d{9})/
        """
    # 2. 检查参数 mobile
    def get(self, request, mobile):
        data = {
            "mobile": mobile,
            "count": Users.objects.filter(mobile=mobile).count()
        }
        return to_json_data(data=data)


class SendSmsCodesView(View):
    # 1. 创建类
    """
    send mobile sms code
    /sms_codes/
    """
    def post(self, request):
        # 2. 获取前端参数
        json_data = request.body
        if not json_data:
            return to_json_data(code=Code.UNKOWNERR, msg="参数有无")
        dict_data = json.loads(json_data.decode("utf8"))

        # mobile = dict_data.get("mobile")
        # text = dict_data.get("text")
        # image_code_id = dict_data.get("image_code_id")

        # todo 通过forms表单校验数据
        # 3. 校验参数  [使用form表单的形式做校验? django restframework 序列化做校验]
        form = CheckImageCodeForm(data=dict_data)
        if form.is_valid():  # todo 直接通过is_valid验证
            # 4. 发送短信验证码
            mobile = form.cleaned_data.get("mobile")
            sms_num = "".join([random.choice(string.digits) for _ in range(6)])  # 通过列表推导式生成6个随机数

            # 5. 保存验证码
            con_redis = get_redis_connection(alias='verify_codes')
            sms_flag_fmt = "sms_flag_{}".format(mobile).encode("utf-8")  # 短信验证码发送记录
            sms_text_fmt = "sms_{}".format(mobile).encode("utf-8")  # 短信验证码key

            # con_redis.setex(sms_flag_fmt, constants.SEND_SMS_CODE_INTERVAL, 1)  # 保存发送记录
            # con_redis.setex(sms_text_fmt, constants.SMS_CODE_REDIS_EXPIRES, sms_num)  # 保存短信验证码

            # todo 通过管道优化执行redis 保存数据
            p1 = con_redis.pipeline()
            try:
                p1.setex(sms_flag_fmt, constants.SEND_SMS_CODE_INTERVAL, 1)  # 保存发送记录
                p1.setex(sms_text_fmt, constants.SMS_CODE_REDIS_EXPIRES, sms_num)  # 保存短信验证码
                p1.execute()
            except (Exception, ) as e:
                logger.error("redis 执行异常 ： {}".format(e))
                return to_json_data(code=Code.UNKOWNERR, msg=error_map[Code.UNKOWNERR])

            # todo 发送短信 使用云通讯

            # 发送短语验证码
            try:
                result = CCP().send_template_sms(mobile,
                                                 [sms_num, constants.SMS_CODE_REDIS_EXPIRES],
                                                 constants.SMS_CODE_TEMP_ID)
            except Exception as e:
                logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
                return to_json_data(errno=Code.SMSERROR, msg=error_map[Code.SMSERROR])
            else:
                if result == 0:
                    logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
                    return to_json_data(errno=Code.OK, msg="短信验证码发送成功")
                else:
                    logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
                    return to_json_data(errno=Code.SMSFAIL, msg=error_map[Code.SMSFAIL])
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            # todo 通过 from.errors 获取到所有的错误信息
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, msg=err_msg_str)
