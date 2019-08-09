import logging

from django_redis import get_redis_connection
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse

from . import constants
from utils.captcha.captcha import captcha
# Create your views here.

# 导入日志器
logger = logging.getLogger("blog")


class ImageCode(View):
    """
    define image verification view
    /image_code/<uuid:image_code_id>/
    """
    # 步骤：
    # 1. todo 创建一个公共类
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
