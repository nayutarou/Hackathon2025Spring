from django.shortcuts import render

# Create your views here.
from django.contrib.auth.forms import UserCreationForm   # ユーザー登録用のフォームクラスをインポート
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm

# SignUpViewクラスを作成
class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('')     # サインアップ成功時、ログインページのURLにリダイレクト
    # 登録するときのhtml
    template_name = 'accounts/signup.html'
    
