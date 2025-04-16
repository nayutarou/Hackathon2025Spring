from django.urls import path
from . import views

app_name = 'attenadces'

urlpatterns = [
    # path('',views.topframe,name='index'),
    # ファイル名指定でも行くように
    # path('',views.topframe,name='top-html'),
    # 出席確認
    # path('',views.attendance,name='attendacnce-html'),
    # 時間割登録
    # path('',views.mytimetable_regist,name='top-html'),
    # 出席登録
    # path('attendances/', views.create_attendances, name='create_attendances'),
    # 単位確認
    # path('',views.credit_check,name='credit_check'),
    # 欠席一覧
    # path('',views.non_attendance_list,name='non_attendance_list'),
]
