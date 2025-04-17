from django.urls import path
from . import views
from .views import syllabus,show_subject_form,subject_register

app_name = 'subjects'

urlpatterns = [
    path("syllabus/", syllabus, name="syllabus"),
    path("register/", show_subject_form, name="show_subject_form"),
    path("registration/", subject_register, name="subject_register")
]
