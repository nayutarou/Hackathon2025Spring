from django.urls import path
from . import views

app_name = 'attendances'

urlpatterns = [
    path('',views.topframe,name='index'),
    # ファイル名指定でも行くように
    path('index/',views.topframe,name='index'),
    # 時間割登録
    path('regist/', views.mytimetable_regist, name='mytimetable_regist'),
    # 出席選択ページ（フォームを表示）
    path('attendance/', views.attendance_page, name='attendance'),
    # 出欠をDBに登録（POST用）
    path('attendance_regist/', views.attendance, name='attendance_regist'),

]
