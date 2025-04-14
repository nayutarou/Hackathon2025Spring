from django.urls import path
from . import views
from .views import syllabus 

app_name = 'subjects'

urlpatterns = [
    path("syllabus/", syllabus, name="syllabus"),
]
