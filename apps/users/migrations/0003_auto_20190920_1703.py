# Generated by Django 2.1.3 on 2019-09-20 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190920_1702'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': '用户个人信息', 'verbose_name_plural': '用户个人信息'},
        ),
        migrations.AlterModelTable(
            name='userprofile',
            table='tb_user_profile',
        ),
    ]
