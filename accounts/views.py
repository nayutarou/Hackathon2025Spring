from django.shortcuts import render

# Create your views here.
from django.contrib.auth.forms import UserCreationForm   # ユーザー登録用のフォームクラスをインポート
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import generic
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User

# root
def root_login_view(request):
    return render(request, 'registration/login.html')

# SignUpViewクラスを作成
class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')     # サインアップ成功時、ログインページのURLにリダイレクト
    # 登録するときのhtml
    template_name = 'register/register.html'
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # email から username を取得
            user = User.objects.get(email=email)
            username = user.username

            # 認証処理（usernameで行う）
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                error = 'メールアドレスまたはパスワードが間違っています。'
        except User.DoesNotExist:
            error = 'メールアドレスまたはパスワードが間違っています。'
        
        return render(request, 'login.html', {'error': error})
    
    return render(request, 'login.html')