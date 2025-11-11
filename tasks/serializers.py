from django.utils import timezone
from rest_framework import serializers

from tasks.models import Employee, Task


class EmployeeSerializer(serializers.ModelSerializer):
    """Сериализатор для CRUD сотрудников."""

    class Meta:
        model = Employee
        fields = "__all__"


class TaskShortSerializer(serializers.ModelSerializer):
    """Сериализатор короткое представление задачи"""

    class Meta:
        model = Task
        fields = ["id", "title", "status", "deadline"]


class TaskSerializer(serializers.ModelSerializer):
    """Основной сериализатор задач."""

    # на запись
    performer = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    # на чтение
    performer_info = EmployeeSerializer(
        source="performer",
        read_only=True,
    )
    # на запись
    parental_task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    # на чтение
    parental_task_info = TaskShortSerializer(
        source="parental_task",
        read_only=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "parental_task",
            "parental_task_info",
            "performer",
            "performer_info",
            "deadline",
            "status",
        ]
        read_only_fields = [
            "id",
        ]

    def validate_deadline(self, value):
        """Проверяет, что срок выполнения задачи не в прошлом."""
        if value is not None and value < timezone.now():
            raise serializers.ValidationError("Срок не может быть в прошлом.")
        return value

    def validate(self, attrs):
        """Общая валидация полей задачи"""
        parental_task = attrs.get("parental_task") or getattr(
            self.instance, "parental_task", None
        )
        if (
            parental_task is not None
            and getattr(self.instance, "id", None) == parental_task.id
        ):
            raise serializers.ValidationError(
                {"parental_task": "Задача не может ссылаться на себя как на родителя."}
            )
        return attrs


class EmployeeWithTasksSerializer(serializers.ModelSerializer):
    """Сериализатор сотрудника с активными задачами."""

    tasks = TaskShortSerializer(many=True, read_only=True)
    active_tasks_count = serializers.IntegerField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "position",
            "active_tasks_count",
            "tasks",
        ]


class ImportantTaskReportSerializer(serializers.Serializer):
    """Сериализатор по важным задачам."""

    task_id = serializers.IntegerField()
    task_title = serializers.CharField()
    deadline = serializers.DateTimeField(allow_null=True)
    employees = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )
