from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from boards.models import Project, Column, Task, TaskComment, ActivityLog
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seeds initial sample data for TaskFlow Kanban application'

    def handle(self, *args, **options):
        self.stdout.write("Seeding TaskFlow demo data...")

        # 1. Create Demo Users
        admin_user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@taskflow.dev'})
        if created:
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write("Created superuser 'admin' with password 'admin123'")

        dev_user, created = User.objects.get_or_create(username='sarah', defaults={'email': 'sarah@taskflow.dev'})
        if created:
            dev_user.set_password('password123')
            dev_user.save()

        # 2. Create Sample Project
        project, created = Project.objects.get_or_create(
            name='SaaS Platform MVP',
            defaults={
                'owner': admin_user,
                'description': 'Building the core microservices, authentication flow, and kanban UI for the new product launch.'
            }
        )
        project.members.add(dev_user)

        # 3. Setup Columns
        if not project.columns.exists():
            project.create_default_columns()

        todo_col = project.columns.get(name='To Do')
        progress_col = project.columns.get(name='In Progress')
        review_col = project.columns.get(name='Review')
        done_col = project.columns.get(name='Done')

        # 4. Create Sample Tasks if none exist
        if not project.tasks.exists():
            t1 = Task.objects.create(
                project=project,
                column=todo_col,
                title='Implement OAuth2 Google & GitHub Sign-In',
                description='Allow users to sign in seamlessly using their existing developer credentials.',
                assignee=dev_user,
                priority='high',
                due_date=date.today() + timedelta(days=5),
                created_by=admin_user,
                position=0
            )

            t2 = Task.objects.create(
                project=project,
                column=todo_col,
                title='Design Dark Mode Color Palette',
                description='Contrast test badges and column cards for WCAG AA compliance.',
                assignee=None,
                priority='low',
                due_date=date.today() + timedelta(days=12),
                created_by=admin_user,
                position=1
            )

            t3 = Task.objects.create(
                project=project,
                column=progress_col,
                title='Drag-and-Drop Kanban Real-time Reordering',
                description='Integrate Sortable.js with Django REST endpoints and save column states on card drop.',
                assignee=dev_user,
                priority='urgent',
                due_date=date.today() + timedelta(days=2),
                created_by=admin_user,
                position=0
            )

            t4 = Task.objects.create(
                project=project,
                column=review_col,
                title='Database Indexing & Query Optimization',
                description='Add prefetch_related for column tasks to eliminate N+1 queries on board load.',
                assignee=admin_user,
                priority='medium',
                due_date=date.today() + timedelta(days=1),
                created_by=dev_user,
                position=0
            )

            t5 = Task.objects.create(
                project=project,
                column=done_col,
                title='Project Scaffolding & Tailwind CSS Base Template',
                description='Set up Django 6 project with authentication, navbar, and card components.',
                assignee=admin_user,
                priority='medium',
                due_date=date.today() - timedelta(days=1),
                created_by=admin_user,
                position=0
            )

            # Comments
            TaskComment.objects.create(
                task=t3,
                author=admin_user,
                content='Sortable.js is working smoothly! Make sure to verify the CSRF token on fetch calls.'
            )
            TaskComment.objects.create(
                task=t3,
                author=dev_user,
                content='Done! CSRF token header is attached and position indexes update automatically.'
            )

            ActivityLog.objects.create(
                project=project,
                user=admin_user,
                action='initialized project board with sample tasks'
            )

        self.stdout.write(self.style.SUCCESS("Sample data successfully seeded!"))

