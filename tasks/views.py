from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from tasks.models import Employee, Task
from tasks.serializers import (EmployeeSerializer, EmployeeWithTasksSerializer,
                               ImportantTaskReportSerializer, TaskSerializer)


class EmployeeViewSet(viewsets.ModelViewSet):
    """CRUD для сотрудников."""

    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all().order_by("id")


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD для задач."""

    serializer_class = TaskSerializer
    queryset = (
        Task.objects.select_related("performer", "parental_task").all().order_by("id")
    )


class BusyEmployeesViewList(ListAPIView):
    """Занятые сотрудники."""

    serializer_class = EmployeeWithTasksSerializer

    def list(self, request, *args, **kwargs):

        employees_data = []

        for employee in Employee.objects.all():
            active_tasks_qs = employee.tasks.filter(
                status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS]
            )
            active_tasks = list(active_tasks_qs)
            active_count = active_tasks_qs.count()

            employees_data.append(
                {
                    "id": employee.id,
                    "full_name": employee.full_name,
                    "position": employee.position,
                    "active_tasks_count": active_count,
                    "tasks": active_tasks,
                }
            )

        employees_data.sort(
            key=lambda item: item["active_tasks_count"],
            reverse=True,
        )

        serializer = self.get_serializer(employees_data, many=True)
        return Response(serializer.data)


class ImportantTasksView(ListAPIView):
    """Важные задачи."""

    serializer_class = ImportantTaskReportSerializer

    def get(self, request, *args, **kwargs):
        important_tasks = Task.objects.exclude(status=Task.Status.IN_PROGRESS).filter(
            parental_task__status=Task.Status.IN_PROGRESS
        )

        employees = list(Employee.objects.all())
        if not employees:
            return Response([])

        employee_load = {}
        for employee in employees:
            active_count = employee.tasks.filter(
                status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS]
            ).count()
            employee_load[employee.id] = (active_count, employee.full_name)

        min_load = min(count for count, _ in employee_load.values())

        least_loaded_ids = [
            emp_id for emp_id, (count, _) in employee_load.items() if count == min_load
        ]

        results = []

        for task in important_tasks:
            candidate_ids = set(least_loaded_ids)

            if task.parental_task.performer_id:
                parent_performer_id: int = task.parental_task.performer_id
                parent_load: int = employee_load.get(parent_performer_id, (0, ""))[0]
                if parent_load <= min_load + 2:
                    candidate_ids.add(parent_performer_id)

            employee_names = [employee_load[eid][1] for eid in candidate_ids]

            results.append(
                {
                    "task_id": task.id,
                    "task_title": task.title,
                    "deadline": task.deadline,
                    "employees": employee_names,
                }
            )

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
