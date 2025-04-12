from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    # emailフィールドを追加（バリデーションも含めて）
    email = forms.EmailField(required=True)

    class Meta:
        model = User  # Djangoがもともと使ってるUserモデル
        fields = ('username', 'email', 'password1', 'password2')  # 使用する項目を定義

    def save(self, commit=True):
        user = super().save(commit=False)  # 親クラスの保存ロジックを一時止める
        user.email = self.cleaned_data['email']  # フォームから取り出したemailを代入
        if commit:
            user.save()  # 保存する
        return user
