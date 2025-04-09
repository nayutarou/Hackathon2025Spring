from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 外部キーのuserid
    subject = models.ForeignKey("subjects.Subject", on_delete=models.CASCADE) # 外部キーのsubject_id
    flag = models.BooleanField(default=False) # 出席欠席のフラグ(デフォルトは欠席)
    created_at = models.DateField(auto_now_add=True) # 日付
    timetable = models.ForeignKey("MYTimetable", on_delete=models.CASCADE) # 外部キーの時間割id

    def __str__(self):
        return f"{self.user.username} - {self.subject.name} - {self.created_at} - {'出席' if self.flag else '欠席'}"


class MYTimetable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 外部キーのuser_id
    week = models.IntegerField()  # 曜日
    lesson = models.IntegerField()  # コマ数
    grade = models.IntegerField()  # 学年
    period = models.BooleanField(default=False)  # 前期後期で分ける

    def __str__(self):
        return f"{self.user.username} - {self.week} - {self.lesson}"