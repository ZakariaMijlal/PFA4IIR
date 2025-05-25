from django.urls import path
from .views import CourseChatView

urlpatterns = [
    path('course/<int:course_id>/', CourseChatView.as_view(), name='course-chat'),
]