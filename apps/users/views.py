from django.views import View
from django.shortcuts import render

# Create your views here.


class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html')