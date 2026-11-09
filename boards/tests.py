import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from boards.models import Project, Column, Task


class TaskFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.client.login(username='testuser', password='testpassword123')

        self.project = Project.objects.create(name='Test Kanban Project', owner=self.user)
        self.project.create_default_columns()
        self.todo_col = self.project.columns.get(name='To Do')
        self.in_progress_col = self.project.columns.get(name='In Progress')

        self.task = Task.objects.create(
            project=self.project,
            column=self.todo_col,
            title='Test Task',
            priority='high',
            created_by=self.user
        )

    def test_project_list_view(self):
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Kanban Project')

    def test_project_board_view(self):
        response = self.client.get(reverse('project_board', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_async_task_move_api(self):
        url = reverse('task_move_api', args=[self.task.id])
        payload = {
            'column_id': self.in_progress_col.id,
            'task_ids_order': [self.task.id]
        }
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.column.id, self.in_progress_col.id)
