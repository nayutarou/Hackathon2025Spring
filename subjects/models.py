from django.db import models
from django.contrib.auth.models import User


class Schedule(models.Model):
    name = models.CharField(max_length=50)  # 開講予定期

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Subject(models.Model):
    subject_name = models.CharField(max_length=50)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    grade_level = models.IntegerField()
    material_cost = models.IntegerField()
    exam_fee = models.IntegerField()
    creadit_maxnum = models.IntegerField()  # その教科のコマ数
    creadit_threshold = models.IntegerField()  # 単位獲得数

    def __str__(self):
        return self.subject_name

class SubjectClass(models.Model):
    MONDAY = 'Mon'
    TUESDAY = 'Tue'
    WEDNESDAY = 'Wed'
    THURSDAY = 'Thu'
    FRIDAY = 'Fri'

    WEEKDAY_CHOICES = [
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    week = models.CharField(max_length=5, choices=WEEKDAY_CHOICES)
    lesson = models.IntegerField()  # コマ数

    class Meta:
        unique_together = ('subject', 'week', 'lesson')

    def __str__(self):
        return f"{self.subject.subject_name} - {self.week} - {self.lesson}"

class Notice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    contents = models.CharField(max_length=50)  # 通知内容
    created_at = models.DateField(auto_now_add=True)  # 作成日

    def __str__(self):
        return f"{self.user.username} - {self.subject.subject_name} - {self.contents}"

class Slack(models.Model):

    name = models.CharField(max_length=50)
    member = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.name} - {self.member}"
