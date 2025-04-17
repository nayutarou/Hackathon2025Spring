from django.urls import path
from . import views
from .views import syllabus,show_subject_form,subject_register,subject_list

app_name = 'subjects'

urlpatterns = [
    path('syllabus/<int:subject_id>/', views.syllabus, name='syllabus_detail'),
    path("register/", show_subject_form, name="show_subject_form"),
    path("registration/", subject_register, name="subject_register"),
    path("list/", subject_list, name="subject_list"),
]
