from django.contrib import admin
from django.urls import path,include
# リダイレクト用の汎用ビューのインポート
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # attendacesフォルダのurls.pyを追跡
    path('attendances/',include('attendances.urls')),
    # トップページの設定
    path('', RedirectView.as_view(url='/attendances/')),
    # ユーザー認証用のビューを呼び出す
    path('accounts/', include('django.contrib.auth.urls')),
    # accounts/以下のルーティングはaccounts.urls.pyに任せる
    path('accounts/', include('accounts.urls')),
]
