from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    path('', views.NewsView.as_view(), name='news'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('banners/', views.BannerView.as_view(), name='banners'),
    path('<int:news_id>/', views.NewsDetailView.as_view(), name='detail'),
    path('<int:news_id>/comments/', views.NewsCommentView.as_view(), name='comment'),
    path("search/", views.SearchView.as_view(), name='search'),
]