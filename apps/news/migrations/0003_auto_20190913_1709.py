# Generated by Django 2.1.3 on 2019-09-13 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20190913_1615'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banner',
            options={'ordering': ['priority', '-update_time', '-id'], 'verbose_name': '轮播图', 'verbose_name_plural': '轮播图'},
        ),
        migrations.AlterField(
            model_name='hotnews',
            name='priority',
            field=models.IntegerField(choices=[(1, '第一级'), (2, '第二级'), (3, '第三级'), (4, '第四级'), (5, '第五级'), (6, '第六级')], default=3, help_text='优先级', verbose_name='优先级'),
        ),
    ]
