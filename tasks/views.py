from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from tasks.models import Employee, Task
from tasks.serializers import EmployeeSerializer, TaskSerializer, EmployeeWithTasksSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all().order_by('id')


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.select_related('performer', 'parental_task').all().order_by('id')


class BusyEmployeesViewList(ListAPIView):
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
                    'id': employee.id,
                    'full_name': employee.full_name,
                    'position': employee.position,
                    'active_tasks_count': active_count,
                    'tasks': active_tasks,
                }
            )

        employees_data.sort(
            key=lambda item: item['active_tasks_count'],
            reverse=True,
        )

        serializer = self.get_serializer(employees_data, many=True)
        return Response(serializer.data)