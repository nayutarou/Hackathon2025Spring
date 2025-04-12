from django.urls import path
from . import views

app_name = 'attenadces'

urlpatterns = [
    path('',views.topframe.as_view(),name='index'),
    # ファイル名指定でも行くように
    path('',views.topframe.as_view(),name='top-html'),
    # 出席確認
    path('',views.attendance.as_view(),name='attendacnce-html'),
    # 時間割登録
    path('',views.mytimetable_regist.as_view(),name='top-html'),
]
