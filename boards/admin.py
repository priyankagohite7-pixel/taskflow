from django.contrib import admin
from .models import Project, Column, Task, TaskComment, ActivityLog


class ColumnInline(admin.TabularInline):
    model = Column
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'description')
    inlines = [ColumnInline]


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'order', 'color')
    list_filter = ('project',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'column', 'priority', 'assignee', 'due_date')
    list_filter = ('priority', 'project', 'column')
    search_fields = ('title', 'description')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'action', 'created_at')
