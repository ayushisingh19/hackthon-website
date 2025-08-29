from django.urls import path
from accounts import views
from django.contrib import admin

app_name = 'accounts'  # namespace define kar rahe hain

urlpatterns = [
     path('admin/', admin.site.urls), 
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('contest/', views.contest, name='contest'),

    # Problem detail view (jo aapko missing lag raha tha)


    # Problem editor with optional slug (for editing existing problem)
    path('editor/', views.problem_editor_view, name='problem_editor'),
    path('editor/<slug:slug>/', views.problem_editor_view, name='problem_editor_with_slug'),

    # API endpoints
    path('submit_code/', views.submit_code, name='submit_code'),
    path('run_code/', views.run_code, name='run_code'),

    # Admin URLs (staff only)
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create_contest/', views.create_contest, name='create_contest'),
    path('delete_contest/', views.delete_contest, name='delete_contest'),
    path('evaluate/', views.partial_evaluate, name='evaluate'),
    path('api/start_evaluation/<int:contest_id>/', views.api_start_evaluation, name='api_start_evaluation'),
    path('api/scoreboard/<int:contest_id>/', views.api_scoreboard, name='api_scoreboard'),
]
