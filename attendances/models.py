from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from subjects.models import SubjectClass,Subject

# 一学年後期とかの学期を格納するためのモデル
class Semester(models.Model):
    name = models.CharField(max_length=50)
    
# 自分の時間割を登録するためのモデル
class MYTimetable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 外部キーのuser_id
    subjectclass = models.ForeignKey(SubjectClass, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subjectclass.subject.subject_name} - {self.semester}"

# 出欠確認のモデル
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 外部キーのuserid
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE) # 外部キーのsubject_id
    flag = models.BooleanField(default=False) # 出席欠席のフラグ(デフォルトは欠席)
    created_at = models.DateField(auto_now_add=True) # 日付
    timetable = models.ForeignKey(MYTimetable, on_delete=models.CASCADE) # 外部キーの時間割id

    def __str__(self):
        return f"{self.user.username} - {self.subject.name} - {self.created_at} - {'出席' if self.flag else '欠席'}"

    