from django import forms
from news.models import News, Tag


class NewsPubForm(forms.ModelForm):
    """
    """
    image_url = forms.URLField(label='文章图片url',
                               error_messages={"required": "文章图片url不能为空"})
    tag = forms.ModelChoiceField(queryset=Tag.objects.only('id').filter(is_delete=False),
                                 error_messages={"required": "文章标签id不能为空", "invalid_choice": "文章标签id不存在", }
                                 )

    class Meta:
        model = News  # 与数据库模型关联
        # 需要关联的字段
        # exclude 排除
        fields = ['title', 'digest', 'content', 'image_url', 'tag']
        error_messages = {
            'title': {
                'max_length': "文章标题长度不能超过150",
                'min_length': "文章标题长度大于1",
                'required': '文章标题不能为空',
            },
            'digest': {
                'max_length': "文章摘要长度不能超过200",
                'min_length': "文章标题长度大于1",
                'required': '文章摘要不能为空',
            },
            'content': {
                'required': '文章内容不能为空',
            },
        }