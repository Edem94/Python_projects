from random import random
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.views.decorators.cache import cache_page
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from .forms import AuthForm, RegisterForm, ProfileForm
from django.contrib.auth.views import LoginView, LogoutView
from .models import Profile
from django.utils.translation import gettext_lazy as _, ngettext


class HelloView(View):
    welcome_message = _('welcome hello world')

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get('items') or 0
        items = int(items_str)
        products_line = ngettext(
            'one product',
            '{count} products',
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"
        )


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin/')

        return render(request, 'myauth/login.html')

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin/')

    return render(request, 'myauth/login.html', {'error': 'Invalid login credentials'})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse('myauth:login'))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response


def another_register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            date_of_birth = form.cleaned_data.get('date_of_birth')
            city = form.cleaned_data.get('city')
            Profile.objects.create(
                user=user,
                city=city,
                date_of_birth=date_of_birth
            )
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'myauth/register.html', {'form': form})


@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f'Cookie value: {value!r} + {random()}')


@permission_required('myauth.view_profile', raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session['foobar'] = 'spameggs'
    return HttpResponse('Session set!')


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get('foobar', 'default')
    return HttpResponse(f'session value: {value!r}')


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})


class UsersListView(ListView):
    template_name = "myauth/users-list.html"
    context_object_name = "users"
    queryset = User.objects.order_by('pk').all()


class UserDetailsView(DetailView):
    template_name = "myauth/user-details.html"
    model = User
    context_object_name = "user"


class ProfileUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "myauth/profile_update_form.html"

    def test_func(self):
        return self.request.user.is_staff or self.request.user.profile == self.get_object()

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse(
            "myauth:user-details",
            kwargs={"pk": self.object.user.pk},
        )
