import logging

from django.http import JsonResponse
from django_redis import get_redis_connection
from django.views import View
from django.http import HttpResponse

from . import constants
from utils.captcha.captcha import captcha
from utils.json_fun import to_json_data
from users.models import Users
# Create your views here.

# 导入日志器
logger = logging.getLogger("blog")


# 1. todo 创建一个公共类
class ImageCode(View):
    """
    define image verification view
    /image_code/<uuid:image_code_id>/
    """
    # 步骤：
    # 2. todo 从前端获取到参数并做验证
    def get(self, request, image_code_id):
        # 3. todo 生成验证码文本和验证码图片
        text, image = captcha.generate_captcha()  # 直接调用，返回文本和图片

        # 4. todo 建立redis连接, 将图片验证码保存到redis 【访问速度快】  key-value 键值对形式
        con_redis = get_redis_connection(alias='verify_codes')  # todo 在settings中配置redis的别名
        img_key = "img_{}".format(image_code_id)  # 构建出键值对的key 的形式
        con_redis.setex(img_key, constants.IMAGE_CODE_REDIS_EXPIRES, text)  # todo 通过con_redis.setex 设置key-time-value

        # 打印日志
        logger.info("image_code: {}".format(text))

        # 5. todo 把验证码图片返回给前端 [HttpResponse]
        return HttpResponse(content=image, content_type='image/jpg')  # 传输图片的时候，接收的是二进制，需要指定content_type为image/jpg 为图片类型


# 1. 创建一个类
class CheckUsernameView(View):
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


# 1. 创建一个类
class CheckMobileView(View):
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
