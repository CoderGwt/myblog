# Generated by Django 2.1.3 on 2019-09-13 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='priority',
            field=models.IntegerField(choices=[(1, '第一级'), (2, '第二级'), (3, '第三级'), (4, '第四级'), (5, '第五级'), (6, '第六级')], default=6, help_text='优先级', verbose_name='优先级'),
        ),
    ]
