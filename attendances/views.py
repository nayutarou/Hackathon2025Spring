import os
import json
import datetime
import logging
import math

from django.conf import settings
from .models import Attendance,MYTimetable,Semester # DBのインポート
from subjects.models import SubjectClass,Subject,Notice,Slack
from django.shortcuts import render,redirect,get_object_or_404,reverse # Djangoのショートカット関数をインポート（renderはテンプレートの表示、redirectはリダイレクト）
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
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
import pytz
from collections import defaultdict

# 登録画面の遷移
@login_required
def attendance_page(request):
    if request.method == 'POST':
        subjectclass_id = request.POST.get('subjectclass_id')
        mytimetable_id = request.POST.get('mytimetable_id')
        lesson = request.POST.get('lesson')
        subject_name = request.POST.get('subject_name')
   
        # 処理を書く
        
        context = {
            'subject_id': subjectclass_id,
            'mytimetable_id': mytimetable_id,
            'lesson': lesson,
            'subject_name': subject_name,
        }
        return render(request, 'attendances/attendance.html', context)

def non_attendance_page(request):
    if request.method == 'POST':
        subjectclass_id = request.POST.get('subjectclass_id')
        mytimetable_id = request.POST.get('mytimetable_id')
        lesson = request.POST.get('lesson')
        subject_name = request.POST.get('subject_name')

        # Slack情報の取得（全件の場合）
        slack_members = Slack.objects.all()




        context = {
            'subject_id': subjectclass_id,
            'mytimetable_id': mytimetable_id,
            'lesson': lesson,
            'subject_name': subject_name,
            'slack_members': slack_members,
        }
        return render(request, 'absence/absence.html', context)

# 登録ボタンでDB登録
@login_required
def attendance(request):
    if request.method == 'POST':
        user = request.user
        # 日本のタイムゾーン
        jst = pytz.timezone('Asia/Tokyo')

        # JSTでの現在の日付を取得
        date = datetime.now(jst).date()



        subject_id = request.POST.get('subject')
        lesson = request.POST.get('lesson')
        week = request.POST.get('week')
        mytimetable_id = request.POST.get('mytimetable_id')

        # 出席情報を登録
        flag = 1 if f'attendance_{subject_id}' in request.POST else 0
        
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
def mytimetable_regist(request):
    semesters = Semester.objects.all()
    user = request.user
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    if request.method == 'POST':
        subject_ids = request.POST.getlist('subject_ids')
        semester_id = request.POST.get('semester_id')

        if not subject_ids:
            messages.warning(request, "科目が選択されていません。")
            return redirect(f"{reverse('attendances:mytimetable_regist')}?semester_id={semester_id}")

        semester = get_object_or_404(Semester, id=semester_id)
        subject_objects = SubjectClass.objects.filter(subject__in=subject_ids)
        timetable_list = [
            MYTimetable(user=user, subjectclass=subject_class, semester=semester)
            for subject_class in subject_objects
        ]

        try:
            MYTimetable.objects.bulk_create(timetable_list)
            messages.success(request, "時間割が正常に登録されました。")
        except IntegrityError:
            messages.error(request, "登録中にエラーが発生しました。既に登録されている可能性があります。")

        return redirect('attendances:index')

    else:
        # GET処理（選択された学期IDがURLに含まれていればそれを使う）
        semester_id = request.GET.get('semester_id')
        selected_semester = get_object_or_404(Semester, id=semester_id) if semester_id else Semester.objects.first()

        # 選択された学期に対して、すでに登録されているか判定
        is_registered = MYTimetable.objects.filter(user=user, semester=selected_semester).exists()

        subject_classes = SubjectClass.objects.all()
        
        
        # 登録済みなら、その時間割を取得してテンプレートに渡す
        mytimetable_list = []
        if is_registered:
            mytimetable_list = MYTimetable.objects.filter(user=user, semester=selected_semester)


        return render(request, 'attendances/mytimetable.html', {
            'subject_classes': subject_classes,
            'semesters': semesters,
            'selected_semester': selected_semester,
            'weekdays': weekdays,
            'is_registered': is_registered,
            'mytimetable_list': mytimetable_list,  # ←追加
        })

    
"""
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 外部キーのuser_id
    subjectclass = models.ForeignKey(SubjectClass, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
"""


# 自分の時間割表示
@login_required
def topframe(request):
    user = request.user
    mytimetable_list = MYTimetable.objects.filter(user=user).select_related('subjectclass', 'semester')
    semester_ids = mytimetable_list.values_list('semester_id', flat=True).distinct()
    my_semesters = Semester.objects.filter(id__in=semester_ids).values('id', 'name')

    week_map = {'1': 'Mon', '2': 'Tue', '3': 'Wed', '4': 'Thu', '5': 'Fri'}

    timetable_data = []
    for timetable in mytimetable_list:
        subjectclass = timetable.subjectclass
        weeks = subjectclass.week if isinstance(subjectclass.week, list) else [subjectclass.week]
        lessons = subjectclass.lesson if isinstance(subjectclass.lesson, list) else [subjectclass.lesson]
        weeks = [week_map.get(str(w), str(w)) for w in weeks]
        schedule_list = list(zip(weeks, lessons))

        timetable_data.append({
            'semester_id': timetable.semester.id,
            'subjectclass_id': subjectclass.id,
            'subject_name': subjectclass.subject.subject_name,
            'schedules': schedule_list,
            'mytimetable_id': timetable.id,
        })

    # --- 通知データの取得 ---
    notices = Notice.objects.filter(user=user).select_related('subject').order_by('-created_at')
    context = {
        'timetable_data': timetable_data,
        'timetable_data_json': json.dumps(timetable_data, cls=DjangoJSONEncoder),
        'semesters': list(my_semesters),
        'weekdays': [1, 2, 3, 4, 5],  # 月〜金
        'periods': range(1, 5),       # 1限〜4限（必要なら調整）
        'notices': notices,           # 通知データを追加
    }

    return render(request, 'attendances/index.html', context)
    
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
            timetable_id = request.POST.get('timetable_id')
            subject_id = request.POST.get('subject_id')
            message = request.POST.get('message')
            slack_id = request.POST.get('teacher')
            absent_lessons = request.POST.getlist('absent_lessons[]')  # ←ここで配列受け取り！
            timetable = get_object_or_404(MYTimetable, pk=timetable_id)
            subject = get_object_or_404(Subject, pk=subject_id)
            print(slack_id)

            # 欠席した各コマに対して Attendance を作成
            for lesson in absent_lessons:
                Attendance.objects.create(
                    user=request.user,
                    subject=subject,
                    flag=True,
                    timetable=timetable,

                )

            # Slack送信（あれば）
            if slack_id:
                try:
                    client.chat_postMessage(channel=slack_id, text=message)
                    result = "success"
                except SlackApiError as e:
                    logging.error(f"Slack error: {e.response['error']}")
                    result = "fail"
            else:
                result = "fail"
                messages.error(request, "Slack IDが未指定です。")

            return redirect('attendances:index')

        except Exception as e:
            messages.error(request, f"エラーが発生しました: {str(e)}")
            return redirect('attendances:index')

    return redirect('attendances:index')

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

    return render(request, 'subjects/credit_confirm.html', {'summary': summary})

#欠席一覧
def non_attendance_list(request):
    try:
        attendances = Attendance.objects.filter(flag=True).select_related('subject').values('subject__subject_name', 'created_at')

        grouped_data = defaultdict(list)
        for item in attendances:
            subject = item['subject__subject_name']
            date = localtime(item['created_at']).strftime('%Y/%m/%d')  # 日付だけ表示
            grouped_data[subject].append(date)

        # 辞書をリスト形式でテンプレートに渡す
        grouped_attendances = [{'subject': subject, 'dates': dates} for subject, dates in grouped_data.items()]

        return render(request, 'abcense/abcense.html', {'attendances': grouped_attendances})

    except Exception as e:
        error_message = f"エラーが発生しました: {str(e)}"
        return HttpResponse(error_message, status=500)
