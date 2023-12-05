from django.urls import path, include
from django.contrib.auth.views import LoginView

from .views import (
    get_cookie_view,
    set_cookie_view,
    set_session_view,
    get_session_view,
    AboutMeView,
    logout_view,
    MyLogoutView,
    RegisterView,
    FooBarView,
    UsersListView,
    UserDetailsView,
    ProfileUpdateView,
    HelloView
)

app_name = "myauth"

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(
            template_name='myauth/login.html',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("hello/", HelloView.as_view(), name="hello"),
    path('cookie/set/', set_cookie_view, name='cookie-set'),
    path('cookie/get/', get_cookie_view, name='cookie-get'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('session/get/', get_session_view, name='get_session'),
    path('session/set/', set_session_view, name='set_session'),
    path('foo-bar/', FooBarView.as_view(), name='foo-bar'),
    path('users/', UsersListView.as_view(), name='users-list'),
    path('users/<int:pk>/', UserDetailsView.as_view(), name='user-details'),
    path("users/<int:pk>/update/", ProfileUpdateView.as_view(), name="profile_update"),
]
