from django.urls import path
from . import views

app_name = 'doc'


urlpatterns = [
    path("index", views.IndexView.as_view(), name="index")
]
