from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.shortcuts import HttpResponse
import json
from accounts.models import CustomUser
from accounts.forms import AuthUserForm, RegisterUserForm


class SignUpView(generic.CreateView):
    model = User
    template_name = 'accounts/signup.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main_page')

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        #form_valid.groups.add(Group.objects.get(name=User))
        aut_user = authenticate(email=email, password=password)     
        login(self.request, aut_user)
        return form_valid
    

class LoginView(LoginView):
    model = User
    template_name = 'accounts/login.html'
    form_class = AuthUserForm
    success_url = reverse_lazy('main_page')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('main_page')


def is_user_exist(request):
    if request.method == 'POST':
        data = request.POST
        print(data)
        is_user = CustomUser.is_user_email(data['mail'])
        data_response = {'result': is_user}
        return HttpResponse(json.dumps(data_response), content_type = 'application/json')
