import os
import json
import datetime

from .models import Attendance,MYTimetable,Semester # DBのインポート
from subjects.models import SubjectClass,Subject,Notice
from django.shortcuts import render,redirect,get_object_or_404 # Djangoのショートカット関数をインポート（renderはテンプレートの表示、redirectはリダイレクト）
from django.contrib.auth.decorators import login_required # ログインしてないユーザを制限する
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,Http404
from django.db import IntegrityError
from django.core.exceptions import SuspiciousOperation
from django.contrib import messages  # フラッシュメッセージ用
from django.views.decorators.csrf import csrf_protect  # CSRF守る
from django.views.decorators.http import require_POST


# 登録画面の遷移
@login_required
def attendance_page(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        lesson = request.POST.get('lesson')
        week = request.POST.get('week')
        mytimetable_id = request.POST.get('mytimetable_id')

        print(f"subjectid={subject_id},lesson={lesson},week={week},mytable_id={mytimetable_id}")
        
        context = {
            'subject_id': subject_id,
            'lesson': lesson,
            'week': week,
            'mytimetable_id': mytimetable_id,
        }
        return render(request, 'attendances/attendance.html', context)


# 登録ボタンでDB登録
@login_required
def attendance(request):
    if request.method == 'POST':
        user = request.user
        date = datetime.date.today()

        subject_id = request.POST.get('subject')
        lesson = request.POST.get('lesson')
        week = request.POST.get('week')
        mytimetable_id = request.POST.get('mytimetable_id')

        # 出席情報を登録
        flag = 1 if f'attendance_{subject_id}' in request.POST else 0
        
        print(f"date={date},subject_id={subject_id},lesson={lesson},week={week},flag={flag},mytimetable={mytimetable_id}")
        
        # Subjectオブジェクトを取得
        subject = get_object_or_404(Subject, id=subject_id)

        # MYTimetableオブジェクトを取得
        mytimetable = get_object_or_404(MYTimetable, id=mytimetable_id)

        Attendance.objects.create(
            user=user,
            subject=subject,
            flag=flag,
            created_at=date,
            timetable=mytimetable
        )

        return redirect('attendances:index')

    return JsonResponse({"error": "POSTメソッドで送ってください"}, status=405)

"""
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 外部キーのuserid
    subject = models.ForeignKey("subjects.Subject", on_delete=models.CASCADE) # 外部キーのsubject_id
    flag = models.BooleanField(default=False) # 出席欠席のフラグ(デフォルトは欠席)
    created_at = models.DateField(auto_now_add=True) # 日付
    timetable = models.ForeignKey("MYTimetable", on_delete=models.CASCADE) # 外部キーの時間割id
"""

# MY時間割 時間割モデルに登録
@login_required
# requestの他にURLからsmester_nameを受け取る\
def mytimetable_regist(request):
    # 全学期を取得（セレクトボックス表示用）
    semesters = Semester.objects.all()

    if request.method == 'POST':
        # 選択された科目ID一覧を取得（チェックボックスから）
        subject_ids = request.POST.getlist('subject_ids')

        # フォームで選ばれた学期のIDを取得（セレクトから）
        semester_id = request.POST.get('semester_id')

        # 科目が選ばれていなければ警告を出してリダイレクト
        if not subject_ids:
            messages.warning(request, "科目が選択されていません。")
            return redirect('mytimetable_regist')  # URL name に合わせてね

        # 学期のオブジェクトを取得（なければ404）
        semester = get_object_or_404(Semester, id=semester_id)

        # 対象のSubjectClassを取得（subject 外部キーに基づく）
        subject_objects = SubjectClass.objects.filter(subject__in=subject_ids)

        # 現在ログイン中のユーザを取得
        user = request.user

        # MYTimetableインスタンスを作成してリストに追加
        timetable_list = [
            MYTimetable(user=user, subjectclass=subject_class, semester=semester)
            for subject_class in subject_objects
        ]

        try:
            # 一括でDBに登録（重複などは例外処理）
            MYTimetable.objects.bulk_create(timetable_list)
            messages.success(request, "時間割が正常に登録されました。")
        except IntegrityError:
            messages.error(request, "登録中にエラーが発生しました。既に登録されている可能性があります。")

        # 登録完了後のリダイレクト先（一覧ページなど）
        return redirect('attendances:index')

    else:
        # GETメソッド時：初期表示で最初の学期を選択状態にする
        default_semester = Semester.objects.first()

        # 曜日のリストをビューで作成
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]

        # 全てのSubjectClassを取得（必要があればここでフィルタも可能）
        subject_classes = SubjectClass.objects.all()

        # テンプレートへ渡すデータ
        return render(request, 'attendances/mytimetable.html', {
            'subject_classes': subject_classes,
            'semesters': semesters,
            'selected_semester': default_semester,
            'weekdays':weekdays,
        })
    
"""
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 外部キーのuser_id
    subjectclass = models.ForeignKey(SubjectClass, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
"""


# 自分の時間割表示
@login_required
def topframe(request):
    # ログインしているユーザー
    user = request.user

    # 学期名に対応する Semester オブジェクトを取得
    semester_name = request.GET.get('semester', '一学年前期')
    semester = get_object_or_404(Semester, name=semester_name)

    # 自分の時間割を取得
    mytimetable_list = MYTimetable.objects.filter(user=user, semester=semester).select_related('subjectclass')

    # 通知を表示
    notice_list = Notice.objects.filter(user=user).order_by('-created_at')

    # 曜日とコマ数（テンプレートでループさせるため）
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    periods = range(1, 5)  # 1限〜4限
    
    # Semesterのリストをテンプレートに渡す
    semesters = Semester.objects.all()
    
    # 追加： lesson × week に対応する item を辞書化
    # timetable_dict = {}
    # for item in mytimetable_list:
    #     key = (item.subjectclass.lesson, item.subjectclass.week)
    #     timetable_dict[key] = item

    return render(request, 'attendances/index.html', {
        'mytimetable_list': mytimetable_list,
        'semester': semester,
        'notice': notice_list,
        'weekdays': weekdays,
        'periods': periods,
        'semesters': semesters,  # ここで学期の一覧を渡す
    })
    
"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    contents = models.CharField(max_length=50)  # 通知内容
    created_at = models.DateField(auto_now_add=True)  # 作成日
"""