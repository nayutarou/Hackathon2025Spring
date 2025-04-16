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


# 出欠確認 Attendanceモデルに登録
@csrf_exempt
@login_required # ログインしている時にできる
def attendance(request):
    try:
        # HTMLからリクエストが送られたかどうか(出欠のボタンが押されたかの確認)
        if request.method != 'POST':
            return JsonResponse({"error": "POST method required"}, status=405)
        

        # HTMLから受け取るもの
        # mytableidの取得
        mytimetable_id = request.POST.get('mytimetable_id')
        # 出欠のflag <- 出欠のフラグ(押されたボタン)
        flag = request.POST.get('flag')
        # 今のコマ
        lesson = request.POST.get('lesson')

        # 必須項目のバリデーション
        # mytimetable_idまたはlessonが取得できないときにエラーページを出す
        if not mytimetable_id or not lesson:
            return JsonResponse({"error": "mytimetable_idとlessonが取得できませんでした"}, status=400)

        # mytimetable_idからMYTimetableに該当する1つのデータを取得
        mytimetable = get_object_or_404(MYTimetable,id=mytimetable_id)
        # mytimetableに格納されているsubjectclass(id)に格納されているsubject(id)を取得
        subject_id = mytimetable.subjectclass.subject
        
        # 今ログインしてるユーザを取得
        user = request.user

        # 今日の曜日
        week = datetime.date.today().weekday() # 月 = 0 火 = 1

        # 今日の日付
        date = datetime.date.today()

        # 他のDBから取得する
        # 時間割id = 今日の曜日から時間割に登録されている今日の押された教科から曜日とコマ数を取得
        # その教科の曜日に合うのを探す、コマもMYTimetableから
        # get_object_or_404(DB名,カラム名 = 調べたいもの ) データベースからオブジェクトを取得する際に使用
        timetables = get_object_or_404(MYTimetable,week = week,lesson = lesson)
        timetable = timetables.id

        Attendance.objects.create(
                user=user,
                sbject=subject_id,
                flag=flag,
                created_at=date,
                timetable=timetable
            )

        # 出欠確認後のリダイレクト先
        return redirect('')

    # JSONのフォーマットが壊れている場合
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    # get_object_or_404() を使ってデータを取得しようとして、該当するデータがデータベースに存在しなかった
    except Http404:
        return JsonResponse({"error": "Timetable not found for today’s subject and lesson."}, status=404)

    # DBに保存するときに、ユニーク制約違反とか、外部キーが壊れてるなどのDB整合性エラーが起きた場合
    except IntegrityError:
        return JsonResponse({"error": "Database error: possibly duplicate or invalid data."}, status=409)

    # データの型や値が期待していた形式と違ったとき。
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid data type or value."}, status=422)

    # Djangoが「セキュリティ的にヤバいリクエストだな」と判断したときに投げられる例外
    except SuspiciousOperation:
        return JsonResponse({"error": "Suspicious operation detected."}, status=400)

    # 上記に当てはまらない 全ての予期しないエラー
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

"""
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 外部キーのuserid
    subject = models.ForeignKey("subjects.Subject", on_delete=models.CASCADE) # 外部キーのsubject_id
    flag = models.BooleanField(default=False) # 出席欠席のフラグ(デフォルトは欠席)
    created_at = models.DateField(auto_now_add=True) # 日付
    timetable = models.ForeignKey("MYTimetable", on_delete=models.CASCADE) # 外部キーの時間割id
"""

# MY時間割 時間割モデルに登録
@login_required
# requestの他にURLからsmester_nameを受け取る
def mytimetable_regist(request,semester_name):
    if request.method == 'POST':
        # チェックボックスからsubject_idからリストの取得とsemesterの取得
        subject_ids = request.POST.getlist('subject_ids')

        # 科目が何も選ばれていなかったときの警告処理
        if not subject_ids:
            messages.warning(request, "科目が選択されていません。")
            return redirect('mytimetable_regist', semester_name=semester_name)

        # URLから学期を取得（見つからなければ404）
        semester = get_object_or_404(Semester, name=semester_name)

        # 一括取得（subject外部キーを元に関連SubjectClassを取得）
        subject_objects = SubjectClass.objects.filter(subject__in=subject_ids)

        # ログインしているユーザを取得
        user = request.user  

        # リストに格納する（各SubjectClassとSemesterでMYTimetableインスタンス作成）
        timetable_list = [
            MYTimetable(user=user, subjectclass=subject_class, semester=semester)
            # 一つずつ取り出す
            for subject_class in subject_objects
        ]

        try:
            # DBに一括登録（例外処理で重複などに備える）
            MYTimetable.objects.bulk_create(timetable_list)
            messages.success(request, "時間割が正常に登録されました。")
        except IntegrityError:
            messages.error(request, "登録中にエラーが発生しました。既に登録されている可能性があります。")

        return redirect('mytimetable')  # 完了後のリダイレクト先（URL nameは適宜修正）

    # GETメソッド時の処理：全てのSubjectClassを取得して表示（必要に応じて絞り込み）
    subject_classes = SubjectClass.objects.all()
    return render(request, 'mytimetable.html', {
        'subject_classes': subject_classes,
        'semester_name': semester_name,
    })
    
"""
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 外部キーのuser_id
    subjectclass = models.ForeignKey(SubjectClass, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
"""


# 自分の時間割表示
@login_required
def topframe(request, semester_name):
    # ログインしているユーザー
    user = request.user

    # 学期名に対応する Semester オブジェクトを取得
    semester = get_object_or_404(Semester, name=semester_name)

    # 自分の時間割を取得
    mytimetable_list = MYTimetable.objects.filter(user=user, semester=semester)

    # 通知を表示
    notice_list = Notice.objects.filter(user=user).order_by('-created_at')

    # テンプレートに渡して描画
    return render(request, 'timetable/mytimetable.html', {
        'mytimetable_list': mytimetable_list,
        'semester': semester,
        'notice':notice_list
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
