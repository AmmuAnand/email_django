from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('signout', views.signout, name="signout"),
    path('activate/<uid64>/<token>', views.activate, name="activate"),
]
