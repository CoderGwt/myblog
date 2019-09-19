from django.urls import path
from . import views

app_name = 'doc'


urlpatterns = [
    path("index", views.IndexView.as_view(), name="index"),
    path('<int:doc_id>/', views.DownloadDocView.as_view(), name='download_doc')
]
