from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as _UserManager

# Create your models here.


class UserManager(_UserManager):
    """
    继承UserManager类，创建超级用户的时候，自定义指定参数，要啥不要啥，全靠代码
    """
    def create_superuser(self, username, password, email=None, **extra_fields):
        super(UserManager, self).create_superuser\
            (username=username, email=email, password=password, **extra_fields)


class Users(AbstractUser):
    """add mobile, email_active field to Django user modules"""

    REQUIRED_FIELDS = ['mobile']

    objects = UserManager()  # 重 objects

    mobile = models.CharField(max_length=11, unique=True, help_text="手机号", verbose_name="手机号",
                              error_messages={
                                  "unique": "手机号已被注册"
                              })
    email_active = models.BooleanField(default=False, verbose_name="邮箱验证状态")

    class Meta:
        db_table = 'tb_users'
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
