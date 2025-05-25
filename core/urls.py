from django.urls import path
from . import views
from chat.views import CourseChatView

urlpatterns = [
    # path('', views.home, name='home'),
    path('', views.dashboard, name='dashboard'),
    path('course/<int:course_id>/', CourseChatView.as_view(), name='course-chat'),

]
