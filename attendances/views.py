import os
import json
import datetime
import logging
import math

from django.conf import settings
from .models import Attendance,MYTimetable,Semester # DBのインポート
from subjects.models import SubjectClass,Subject,Notice
from django.shortcuts import render,redirect,get_object_or_404 # Djangoのショートカット関数をインポート（renderはテンプレートの表示、redirectはリダイレクト）
from django.contrib.auth.decorators import login_required # ログインしてないユーザを制限する
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,Http404,HttpResponse
from django.db import IntegrityError
from django.core.exceptions import SuspiciousOperation
from django.contrib import messages  # フラッシュメッセージ用
from django.views.decorators.csrf import csrf_protect  # CSRF守る
from django.views.decorators.http import require_POST
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from django.db.models import *





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
# 出席登録
@login_required
def create_attendances(request):
    if request.method == 'GET':
        try:
            timetable_id = request.GET.get('timetable_id')
            subject_id = request.GET.get('subject_id')

            timetable = get_object_or_404(MYTimetable, pk=timetable_id)
            subject = get_object_or_404(Subject, pk=subject_id)

            Attendance.objects.create(
                user=request.user,
                subject=subject,
                flag=False,  # 出席として登録
                timetable=timetable
            )

            return redirect('attendance_list')  # 成功時はリダイレクト

        except Exception as e:
            return HttpResponse(f'エラーが発生しました: {str(e)}', status=400)

    return HttpResponse('無効なリクエストメソッドです。', status=405)
# 欠席登録とslackのDM送信
# Slackクライアントの初期化
client = WebClient(token=settings.SLACK_BOT_TOKEN)

@login_required
def create_attendance(request):
    if request.method == 'POST':
        try:
            timetable_id = request.POST.get('timetable_id')  # POSTパラメータから取得
            subject_id = request.POST.get('subject_id')      # 科目POSTパラメータから取得
            message = request.POST.get('message')            # メッセージをPOSTから取得
            slack_id = request.POST.get('slack_id')          # Slack IDをPOSTから取得

            if not message:
                messages.error(request, "メッセージが未入力です。")
                return redirect('attendance_list')  # メッセージ未入力の場合はリダイレクト

            timetable = get_object_or_404(MYTimetable, pk=timetable_id)
            subject = get_object_or_404(Subject, pk=subject_id)

            # 出席情報を作成
            attendance = Attendance.objects.create(
                user=request.user,
                subject=subject,
                flag=True,  # 出席フラグをTrueに設定
                timetable=timetable
            )

            # Slack IDがPOSTリクエストから送信されてきた場合にSlackにDMを送信
            if slack_id:
                try:
                    # Slackにメッセージ送信
                    client.chat_postMessage(channel=slack_id, text=message)
                    result = "success"
                except SlackApiError as e:
                    logging.error(f"Slack error: {e.response['error']}")
                    result = "fail"
            else:
                result = "fail"
                messages.error(request, "Slack IDが未指定です。")

            return redirect('attendance_list')  # 登録後に遷移

        except Exception as e:
            messages.error(request, f"エラーが発生しました: {str(e)}")
            return redirect('attendance_list')  # エラー後は一覧ページにリダイレクト

    return redirect('home')  # GET以外リダイレクト

# 単位確認
@login_required
def credit_check(request):
    user = request.user

    # 教科ごとに出席・欠席を集計
    summary_raw = (
        Attendance.objects
        .filter(user=user)
        .values('subject__id', 'subject__subject_name')  # 教科ごと
        .annotate(
            attended_count=Count('id', filter=Q(flag=False)),  # 出席（flag=False）
            absent_count=Count('id', filter=Q(flag=True))       # 欠席（flag=True）
        )
    )

    summary = []
    for row in summary_raw:
        total = row['attended_count'] + row['absent_count']
        attendance_ratio = math.floor((row['attended_count'] / total) * 100) if total > 0 else 0

        summary.append({
            'subject_id': row['subject__id'],
            'subject_name': row['subject__subject_name'],
            'attended_count': row['attended_count'],
            'absent_count': row['absent_count'],
            'total': total,
            'attendance_ratio': attendance_ratio,
        })

    return render(request, 'attendance_summary.html', {'summary': summary})

#欠席一覧
def non_attendance_list(request):
    try:
        attendances = Attendance.objects.filter(flag=True).select_related('subject').values('subject__subject_name', 'created_at')
        return render(request, 'attendance_summary.html', {'attendances': attendances})

    except Exception as e:
        error_message = f"エラーが発生しました: {str(e)}"
        return HttpResponse(error_message, status=500)
