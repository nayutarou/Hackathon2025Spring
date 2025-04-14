from django.urls import path
from . import views
from .views import login_view

app_name = 'accounts'

urlpatterns = [
    path('register/', views.SignUpView.as_view(), name='signup'), # サインアップページ
    path("login/", login_view, name="login"),
    path("", login_view, name="root-login"),
]