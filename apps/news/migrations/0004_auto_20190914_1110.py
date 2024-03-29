# Generated by Django 2.1.3 on 2019-09-14 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_auto_20190913_1709'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='hotnews',
            options={'ordering': ['priority', '-update_time', '-id'], 'verbose_name': '热门新闻', 'verbose_name_plural': '热门新闻'},
        ),
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='news.Comment'),
        ),
    ]
