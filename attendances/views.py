from django.shortcuts import render
from django.http import JsonResponse
from .models import Attendance, MYTimetable, User, Subject
from django.utils import timezone
from django.db import IntegrityError, DatabaseError

def create_attendance(request):
    try:
        user = User.objects.get(id=1)  # 例：ユーザID=1
        subject = Subject.objects.get(id=1)  # 例：教科ID=1
        timetable = MYTimetable.objects.get(timetable_id=1)  # 時間割ID=1

        attendance = Attendance.objects.create(
            attendance_id=123,  # すでにPK指定する場合
            user_id=user,
            subject_id=subject,
            flag=True,
            created_at=timezone.now().date(),
            timetable_id=timetable
        )

        return JsonResponse({"status": "success", "message": "出席を登録しました"})

    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "ユーザーが存在しません"})

    except Subject.DoesNotExist:
        return JsonResponse({"status": "error", "message": "教科が存在しません"})

    except MYTimetable.DoesNotExist:
        return JsonResponse({"status": "error", "message": "時間割が存在しません"})

    except IntegrityError:
        return JsonResponse({"status": "error", "message": "出席IDが重複しています"})

    except DatabaseError:
        return JsonResponse({"status": "error", "message": "データベースエラーが発生しました"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"予期せぬエラー: {str(e)}"})
