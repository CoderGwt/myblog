from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    path('index', views.IndexView.as_view(), name='index'),
    path("search", views.SearchView.as_view(), name='search'),
]