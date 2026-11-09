import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q

from .models import Project, Column, Task, TaskComment, ActivityLog
from .forms import RegisterForm, ProjectForm, TaskForm, ColumnForm, TaskCommentForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('project_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to TaskFlow, {user.username}!")
            return redirect('project_list')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def project_list(request):
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().order_by('-updated_at')
    form = ProjectForm()
    return render(request, 'boards/project_list.html', {
        'projects': projects,
        'form': form,
    })


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.create_default_columns()
            ActivityLog.objects.create(
                project=project,
                user=request.user,
                action=f"created project '{project.name}'"
            )
            messages.success(request, f"Project '{project.name}' created with default Kanban columns!")
            return redirect('project_board', project_id=project.id)
    return redirect('project_list')


@login_required
def project_board(request, project_id):
    project = get_object_or_404(
        Project.objects.prefetch_related('columns__tasks__assignee', 'columns__tasks__comments'),
        id=project_id
    )
    # Check authorization
    if project.owner != request.user and request.user not in project.members.all():
        return HttpResponseForbidden("You do not have access to this project.")

    task_form = TaskForm(project=project)
    column_form = ColumnForm()
    comment_form = TaskCommentForm()
    activities = project.activities.all()[:15]
    available_users = User.objects.exclude(id__in=[project.owner.id] + list(project.members.values_list('id', flat=True)))

    return render(request, 'boards/board.html', {
        'project': project,
        'columns': project.columns.all(),
        'task_form': task_form,
        'column_form': column_form,
        'comment_form': comment_form,
        'activities': activities,
        'available_users': available_users,
    })


@login_required
@require_POST
def project_add_member(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return HttpResponseForbidden("Only the project owner can add team members.")
    user_id = request.POST.get('user_id')
    if user_id:
        user_to_add = get_object_or_404(User, id=user_id)
        project.members.add(user_to_add)
        ActivityLog.objects.create(
            project=project,
            user=request.user,
            action=f"added {user_to_add.username} to the project team"
        )
        messages.success(request, f"Added {user_to_add.username} to team.")
    return redirect('project_board', project_id=project.id)


@login_required
@require_POST
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return HttpResponseForbidden("Only the project owner can delete this project.")
    project_name = project.name
    project.delete()
    messages.success(request, f"Project '{project_name}' was deleted.")
    return redirect('project_list')


@login_required
@require_POST
def column_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user and request.user not in project.members.all():
        return HttpResponseForbidden("Not authorized.")
    form = ColumnForm(request.POST)
    if form.is_valid():
        column = form.save(commit=False)
        column.project = project
        column.order = project.columns.count()
        column.save()
        ActivityLog.objects.create(
            project=project,
            user=request.user,
            action=f"added new column '{column.name}'"
        )
        messages.success(request, f"Column '{column.name}' created.")
    return redirect('project_board', project_id=project.id)


@login_required
@require_POST
def column_delete(request, column_id):
    column = get_object_or_404(Column, id=column_id)
    project = column.project
    if project.owner != request.user:
        return HttpResponseForbidden("Only the project owner can delete columns.")
    col_name = column.name
    column.delete()
    ActivityLog.objects.create(
        project=project,
        user=request.user,
        action=f"deleted column '{col_name}'"
    )
    messages.success(request, f"Column '{col_name}' removed.")
    return redirect('project_board', project_id=project.id)


@login_required
@require_POST
def task_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user and request.user not in project.members.all():
        return HttpResponseForbidden("Not authorized.")
    form = TaskForm(request.POST, project=project)
    if form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.created_by = request.user
        task.position = task.column.tasks.count()
        task.save()
        ActivityLog.objects.create(
            project=project,
            user=request.user,
            action=f"created task '{task.title}' in {task.column.name}"
        )
        messages.success(request, f"Task '{task.title}' created.")
    return redirect('project_board', project_id=project.id)


@login_required
@require_POST
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project
    if project.owner != request.user and request.user not in project.members.all():
        return HttpResponseForbidden("Not authorized.")
    title = task.title
    task.delete()
    ActivityLog.objects.create(
        project=project,
        user=request.user,
        action=f"deleted task '{title}'"
    )
    messages.success(request, f"Task '{title}' deleted.")
    return redirect('project_board', project_id=project.id)


@login_required
def task_detail_api(request, task_id):
    task = get_object_or_404(Task.objects.select_related('column', 'assignee', 'created_by'), id=task_id)
    project = task.project
    if project.owner != request.user and request.user not in project.members.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    comments = [
        {
            'author': c.author.username,
            'content': c.content,
            'created_at': c.created_at.strftime('%b %d, %Y %H:%M')
        }
        for c in task.comments.all()
    ]

    return JsonResponse({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'priority': task.priority,
        'column_id': task.column.id,
        'column_name': task.column.name,
        'assignee': task.assignee.username if task.assignee else 'Unassigned',
        'assignee_id': task.assignee.id if task.assignee else None,
        'due_date': str(task.due_date) if task.due_date else '',
        'created_by': task.created_by.username if task.created_by else 'Unknown',
        'created_at': task.created_at.strftime('%b %d, %Y'),
        'comments': comments
    })


@login_required
@require_POST
def task_move_api(request, task_id):
    """
    Receives JSON: { column_id: int, new_position: int, task_ids_order: list[int] }
    Updates the task column and reorders tasks.
    """
    try:
        data = json.loads(request.body)
        new_column_id = data.get('column_id')
        task_ids_order = data.get('task_ids_order', [])

        task = get_object_or_404(Task, id=task_id)
        project = task.project
        if project.owner != request.user and request.user not in project.members.all():
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        new_column = get_object_or_404(Column, id=new_column_id, project=project)
        old_column_name = task.column.name
        new_column_name = new_column.name

        task.column = new_column
        task.save()

        # Update positions according to client order
        for idx, tid in enumerate(task_ids_order):
            Task.objects.filter(id=tid, project=project).update(position=idx)

        if old_column_name != new_column_name:
            ActivityLog.objects.create(
                project=project,
                user=request.user,
                action=f"moved '{task.title}' from {old_column_name} to {new_column_name}"
            )

        return JsonResponse({'status': 'success', 'task_id': task.id, 'column': new_column_name})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_POST
def task_comment_add(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project
    if project.owner != request.user and request.user not in project.members.all():
        return HttpResponseForbidden("Not authorized.")
    form = TaskCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.task = task
        comment.author = request.user
        comment.save()
        ActivityLog.objects.create(
            project=project,
            user=request.user,
            action=f"commented on task '{task.title}'"
        )
        messages.success(request, "Comment added.")
    return redirect('project_board', project_id=project.id)
