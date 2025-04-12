from django.contrib import admin
from .models import Attendance,MYTimetable,Semester
# Register your models here.


admin.site.register(Attendance,MYTimetable,Semester)