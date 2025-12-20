from django.urls import path
from rest_framework import routers

from tasks.apps import TasksConfig
from tasks.views import (BusyEmployeesViewList, EmployeeViewSet,
                         ImportantTasksView, TaskViewSet)

app_name = TasksConfig.name

router = routers.DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path(
        "tasks/busy_employees/", BusyEmployeesViewList.as_view(), name="busy-employees"
    ),
    path(
        "tasks/important_tasks/", ImportantTasksView.as_view(), name="important-tasks"
    ),
] + router.urls
