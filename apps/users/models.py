import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as _UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save  # 数据库模型save之后调用post_save()信号


from utils.models import ModelBase


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


class UserProfile(ModelBase):
    """create user profile model"""
    GENDER_CHOICES = [
        ('M', "男"),
        ('F', '女')
    ]
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='user_profile')
    nickname = models.TextField(max_length=100, null=True, blank=True, verbose_name="昵称", help_text="昵称")
    born_date = models.DateField(null=True, blank=True, verbose_name="出生日期", help_text="出生日期")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M", verbose_name="性别", help_text="性别")
    motto = models.TextField(max_length=1024, null=True, blank=True, verbose_name="座右铭", help_text="座右铭")

    class Meta:
        db_table = 'tb_user_profile'
        verbose_name = "用户个人信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname


@receiver(signal=post_save, sender=Users)
def create_user_profile(sender, **kwargs):
    """create user profile function"""
    print(kwargs)
    if kwargs.get("created", False):
        user_profile = UserProfile.objects.get_or_create(user=kwargs.get('instance'))
        if user_profile[-1]:
            user_profile = user_profile[0]
            user_profile.nickname = "信号机制"
            user_profile.born_date = datetime.date(2019, 12, 2)
            user_profile.motto = "django signal is easy to learn"
            user_profile.save()