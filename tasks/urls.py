from django.urls import path

from tasks.apps import TasksConfig
from rest_framework import routers

from tasks.views import EmployeeViewSet, TaskViewSet, BusyEmployeesViewList

app_name = TasksConfig.name

router = routers.DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path(
        "tasks/busy_employees/", BusyEmployeesViewList.as_view(), name="busy-employees"
    ),
] + router.urls
