from django.views import View
from django.shortcuts import render
from django.http import Http404

from .models import Teacher, Course, CourseCategory


class IndexView(View):
    def get(self, request):
        courses = Course.objects.only('title', 'cover_url', 'teacher__name', 'teacher__positional_title')\
            .filter(is_delete=False)
        return render(request, 'course/course.html', locals())


class CourseDetailView(View):
    """
    create course detail view
    route: /course/<int:couse_id>/
    """
    def get(self, request, course_id):
        course = Course.objects.only(
            "title", 'cover_url', 'profile', 'outline', 'teacher__name',
            'teacher__avatar_url', 'teacher__positional_title', 'teacher__profile')\
            .select_related('teacher')\
            .filter(is_delete=False, id=course_id).first()
        if not course:
            raise Http404("课程不存在")

        return render(request, 'course/course_detail.html', locals())

