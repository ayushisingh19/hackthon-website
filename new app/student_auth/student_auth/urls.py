from django.urls import path
from accounts import views
from django.contrib import admin
from accounts import views

urlpatterns = [
     path('admin/', admin.site.urls), 
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('contest/', views.contest, name='contest'),




    # Problem editor with optional slug (for editing existing problem)
     path("start/", views.start, name="start"),   # Start page with all problems
    path("start/<int:id>/", views.start, name="problem_detail"),
    path('run_code/<int:problem_id>/', views.run_code, name='run_code'),



    # API endpoints
   


    # Admin URLs (staff only)
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create_contest/', views.create_contest, name='create_contest'),
    path('delete_contest/', views.delete_contest, name='delete_contest'),
    path('evaluate/', views.partial_evaluate, name='evaluate'),
    path("problems/<int:problem_id>/visible-testcases/", views.get_visible_testcases, name="get_visible_testcases"),

]
