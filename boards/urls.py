from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Projects
    path('', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/', views.project_board, name='project_board'),
    path('projects/<int:project_id>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:project_id>/members/add/', views.project_add_member, name='project_add_member'),

    # Columns
    path('projects/<int:project_id>/columns/create/', views.column_create, name='column_create'),
    path('columns/<int:column_id>/delete/', views.column_delete, name='column_delete'),

    # Tasks
    path('projects/<int:project_id>/tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/comments/add/', views.task_comment_add, name='task_comment_add'),

    # JSON APIs for Kanban Drag-Drop & Quick View
    path('api/tasks/<int:task_id>/', views.task_detail_api, name='task_detail_api'),
    path('api/tasks/<int:task_id>/move/', views.task_move_api, name='task_move_api'),
]

