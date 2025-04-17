from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import login_view

app_name = 'accounts'

urlpatterns = [
    path('register/', views.SignUpView.as_view(), name='signup'), # サインアップページ
    path("login/", login_view, name="login"),
    path("", login_view, name="root-login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
     # パスワードリセット機能（Django組み込み）
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]