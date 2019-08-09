from django.urls import path
from . import views

app_name = 'verification'

urlpatterns = [
    path("image_code/<uuid:image_code_id>/", views.ImageCode.as_view(), name='image_code')
]