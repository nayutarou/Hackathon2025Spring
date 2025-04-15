import os
import json
import datetime

from attendances.models import Attendance,MYTimetable,Semester # DBのインポート
from .models import SubjectClass,Subject,Notice
from django.shortcuts import render,redirect,get_object_or_404 # Djangoのショートカット関数をインポート（renderはテンプレートの表示、redirectはリダイレクト）
from django.contrib.auth.decorators import login_required # ログインしてないユーザを制限する
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
# Create your views here.



@csrf_exempt
@login_required # ログインしている時にできる
# @require_POST # POSTじゃなければ405返す
def syllabus(request):
    try:
        # HTMLからリクエストが送られたかどうか(出欠のボタンが押されたかの確認)
        if request.method != 'POST':
            return JsonResponse({"error": "POST method required"}, status=405)
        
        # htmlから受け取る
        subject_id = request.POST.get('subject_id')
        if not subject_id:
            return JsonResponse({"error": "subject_idが取得できませんでした"}, status=400)

        subject = get_object_or_404(Subject, subject=subject_id)
        subjectclass = SubjectClass.objects.filter(subject=subject)

        return render(request, 'subjects/syllabus.html', {
            'subject': subject,
            'subjectclass': subjectclass,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)