from django.urls import path, re_path
from . import views

app_name = 'verification'

urlpatterns = [
    path("image_code/<uuid:image_code_id>/", views.ImageCode.as_view(), name='image_code'),
    re_path('username/(?P<username>\w{5,20})/', views.CheckUsernameView.as_view(), name='check_username'),
    re_path("mobiles/(?P<mobile>1[3-9]\d{9})/", views.CheckMobileView.as_view(), name='check_mobile')
]