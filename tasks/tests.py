from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Employee, Task

User = get_user_model()
Future = timezone.now() + timedelta(days=1)


class BaseAPITestCase(APITestCase):
    """Базовый класс, создающий пользователя и авторизацию."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
        )
        self.client.force_authenticate(user=self.user)


class EmployeeViewSetTests(BaseAPITestCase):
    """Тесты API для сотрудников."""

    def test_create_employee(self):
        url = "/api/employees/"
        data = {
            "full_name": "Иванов Иван",
            "position": "Dev",
            "email": "ivanov@example.com",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.first().full_name, "Иванов Иван")

    def test_list_employees(self):
        Employee.objects.create(full_name="A", position="Dev")
        Employee.objects.create(full_name="B", position="QA")

        url = "/api/employees/"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # с пагинацией DRF ответ в виде {count, next, previous, results}
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)


class TaskViewSetTests(BaseAPITestCase):
    """Тесты API для задач."""

    def setUp(self) -> None:
        super().setUp()
        self.employee = Employee.objects.create(
            full_name="Исполнитель",
            position="Dev",
        )

    def test_create_task(self):
        url = "/api/tasks/"
        data = {
            "title": "Новая задача",
            "performer": self.employee.id,
            "status": Task.Status.NEW,
            "deadline": Future,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.first()
        self.assertEqual(task.title, "Новая задача")
        self.assertEqual(task.performer, self.employee)

    def test_retrieve_task_contains_performer_info(self):
        task = Task.objects.create(
            title="Задача",
            performer=self.employee,
            status=Task.Status.NEW,
            deadline= Future,
        )
        url = f"/api/tasks/{task.id}/"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("performer_info", response.data)
        self.assertEqual(response.data["performer_info"]["id"], self.employee.id)


class BusyEmployeesViewTests(BaseAPITestCase):
    """Тесты отчёта 'Занятые сотрудники'."""

    def setUp(self) -> None:
        super().setUp()
        self.emp1 = Employee.objects.create(full_name="Мало задач", position="Dev")
        self.emp2 = Employee.objects.create(full_name="Много задач", position="Dev")

        # сотрудник 1 - 1 задача
        Task.objects.create(
            title="t1",
            performer=self.emp1,
            status=Task.Status.NEW,
            deadline=Future,
        )

        # сотрудник 2 - 2 задачи
        Task.objects.create(
            title="t2",
            performer=self.emp2,
            status=Task.Status.NEW,
            deadline=Future,
        )
        Task.objects.create(
            title="t3",
            performer=self.emp2,
            status=Task.Status.IN_PROGRESS,
            deadline=Future,
        )

    def test_busy_employees(self):
        url = "/api/tasks/busy_employees/"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data

        # сотрудник 2 должен быть первым (2 задачи), затем сотрудник 1 (1 задача)
        self.assertGreaterEqual(len(results), 2)
        self.assertEqual(results[0]["full_name"], "Много задач")
        self.assertEqual(results[0]["active_tasks_count"], 2)
        self.assertEqual(results[1]["full_name"], "Мало задач")
        self.assertEqual(results[1]["active_tasks_count"], 1)


class ImportantTasksViewTests(BaseAPITestCase):
    """Тесты отчёта 'Важные задачи'."""

    def setUp(self) -> None:
        super().setUp()
        self.emp1 = Employee.objects.create(full_name="Мало задач", position="Dev")
        self.emp2 = Employee.objects.create(
            full_name="Исполнитель родителя", position="Dev"
        )

        # сотрудник 1 — 0 активных задач, сотрудник 2 — 1 активная
        self.parent_task = Task.objects.create(
            title="Родительская задача",
            performer=self.emp2,
            status=Task.Status.IN_PROGRESS,
            deadline=Future,
        )

        # важная подзадача
        self.important_subtask = Task.objects.create(
            title="Важная подзадача",
            status=Task.Status.NEW,
            parental_task=self.parent_task,
            deadline=Future,
        )

    def test_important_tasks_report(self):
        url = "/api/tasks/important_tasks/"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data

        self.assertGreaterEqual(len(results), 1)
        titles = [item["task_title"] for item in results]
        self.assertIn("Важная подзадача", titles)

        # проверяем
        important_item = next(
            item for item in results if item["task_title"] == "Важная подзадача"
        )
        self.assertIsInstance(important_item["employees"], list)
        self.assertTrue(len(important_item["employees"]) >= 1)
