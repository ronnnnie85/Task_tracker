from tasks.apps import TasksConfig
from rest_framework import routers

from tasks.views import EmployeeViewSet, TaskViewSet

app_name = TasksConfig.name

router_employee = routers.DefaultRouter()
router_employee.register(r'employees', EmployeeViewSet, basename='employee')

router_task = routers.DefaultRouter()
router_task.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [

] + router_employee.urls + router_task.urls

