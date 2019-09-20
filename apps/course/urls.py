from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path("index", views.IndexView.as_view(), name='index'),
    path("<int:course_id>/", views.CourseDetailView.as_view(), name='course_detail'),
]