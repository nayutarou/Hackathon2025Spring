import os
import json
import datetime

from models import Attendance,MYTimetable # DBのインポート
# from subjects.models import SubjectClass
from django.shortcuts import render,redirect,get_object_or_404 # Djangoのショートカット関数をインポート（renderはテンプレートの表示、redirectはリダイレクト）
from django.contrib.auth.decorators import login_required # ログインしてないユーザを制限する
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,Http404
from django.db import IntegrityError
from django.core.exceptions import SuspiciousOperation

# 出欠確認 Attendanceモデルに登録
@csrf_exempt
@login_required # ログインしている時にできる
def attendance(request):
    try:
        # HTMLからリクエストが送られたかどうか(出欠のボタンが押されたかの確認)
        if request.method != 'POST':
            return JsonResponse({"error": "POST method required"}, status=405)
        
        # HTTPリクエストの中身(body)を取得
        # body = json.loads(request.body)

        # HTMLから受け取るとこ
        # subjectidの取得 <- 押されたsubjectのidを取得する(時間割のモデルと関数、htmlを書かないと無理?)
        subject = request.POST.get('subject_id')
        # 出欠のflag <- 出欠のフラグ(押されたボタン)
        flag = request.POST.get('flag')
        # 今のコマ
        lesson = request.POST.get('lesson')

        # 必須項目のバリデーション
        # subject_idまたはlessonが取得できないときにエラーページを出す
        if not subject or not lesson:
            return JsonResponse({"error": "Subject and Lesson are required"}, status=400)

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
        timetable = get_object_or_404(MYTimetable,week = week,lesson = lesson)

        Attendance.objects.create(
                user=user,
                sbject=subject,
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

