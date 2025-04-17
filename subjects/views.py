import os
import json
import datetime
import math
from attendances.models import Attendance,MYTimetable,Semester # DBのインポート
from .models import SubjectClass,Subject,Notice
from django.shortcuts import render,redirect,get_object_or_404 # Djangoのショートカット関数をインポート（renderはテンプレートの表示、redirectはリダイレクト）
from django.contrib.auth.decorators import login_required # ログインしてないユーザを制限する
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import HttpResponse
# Create your views here.



@csrf_exempt
@login_required # ログインしている時にできる
def syllabus(request, subject_id):
    try:
        # subject_id を使って Subject モデルから取得
        subject = get_object_or_404(Subject, pk=subject_id)

        # 該当する Subject に紐づく SubjectClass を取得
        subject_classes = Subject.objects.filter(id=subject_id)
        print(subject)
        return render(request, 'subjects/syllabus.html', {
            'subject': subject,
            'subjectclass': subject_classes,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def subject_register(request):
    if request.method == 'POST':
        try:
            subject_name = request.POST.get('subject_name')
            schedule_id = request.POST.get('schedule_id')
            category_id = request.POST.get('category_id')
            grade_level = request.POST.get('grade_leval')
            material_cost = request.POST.get('material_cost')
            exam_fee = request.POST.get('exam_fee')
            creadit_maxnum = request.POST.get('creadit_maxnum')
            creadit_threshold = request.POST.get('creadit_threshold')
            weeks = request.POST.getlist('week[]')  # weekのリスト
            nums = request.POST.getlist('num[]')    # lesson数のリスト
            print(weeks)
            print(nums)
            # 数値変換
            creadit_maxnum = float(creadit_maxnum)
            creadit_minnum = math.floor(creadit_maxnum * 0.2)

            # Subjectの作成
            subject = Subject.objects.create(
                subject_name=subject_name,
                schedule_id=schedule_id,
                category_id=category_id,
                grade_level=grade_level,
                material_cost=material_cost,
                exam_fee=exam_fee,
                creadit_maxnum=creadit_maxnum,
                creadit_threshold=creadit_threshold,
                creadit_minnum=creadit_minnum
            )

            # SubjectClassに複数レコード作成
            subject_classes = []
            for week, num in zip(weeks, nums):
                subject_classes.append(
                    SubjectClass(subject_id=subject.id, week=week, lesson=num)
                )
            SubjectClass.objects.bulk_create(subject_classes)

            return redirect('subjects:syllabus')

        except Exception as e:
            return HttpResponse(f"エラーが発生しました: {str(e)}", status=500)

    return render(request, 'subject_form.html')

#授業登録のためにcategoryとscheduleを取得
from django.shortcuts import render
from .models import Category, Schedule

def show_subject_form(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        schedules = Schedule.objects.all()
        context = {
            'categories': categories,
            'schedules': schedules,
        }
        return render(request, 'subjects/subject_form.html', context)
    
    return HttpResponse(status=405)  # POST以外は許可しない

@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'list/list.html', {'subjects': subjects})
