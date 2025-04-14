from django.contrib import admin
from django.urls import path,include
from django.urls import path
from accounts.views import login_view,root_login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    # accounts/以下のルーティングはaccounts.urls.pyに任せる
    path('',root_login_view,name='root-login'),
    # path('attendances/',include('attendances.urls')),
    path('accounts/', include('accounts.urls')),
    # ユーザー認証用のビューを呼び出す
    path('accounts/', include('django.contrib.auth.urls')),
]
