from django.db import models


class ModelBase(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, verbose_name="逻辑删除")

    class Meta:
        # 指定为抽象类，用于其他model类继承，数据库迁移的时候不会创建该表
        abstract = True