from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('contest/', views.contest, name='contest'),
    path('problem/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('editor/', views.problem_editor_view, name='problem_editor'),
    path('editor/<slug:slug>/', views.problem_editor_view, name='problem_editor_with_slug'),
        path('problem/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    
]
