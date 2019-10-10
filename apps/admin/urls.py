from django.urls import path

from . import views

app_name = 'admin'

urlpatterns = [
    path("index/", views.IndexView.as_view(), name='index'),
    path('tags/', views.TagManageView.as_view(), name='tags'),
    path('tags/<int:tag_id>/', views.TagEditView.as_view(), name='tags_manage'),

    path("news/", views.NewsManageView.as_view(), name='news_manage'),
]