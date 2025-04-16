from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Category)
admin.site.register(Subject)
admin.site.register(SubjectClass)
admin.site.register(Notice)
admin.site.register(Slack)
admin.site.register(Schedule)