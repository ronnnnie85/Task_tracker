from django.db import models


class Employee(models.Model):
    full_name = models.CharField(
        max_length=500,
        verbose_name="ФИО сотрудника",
        help_text="Укажите ФИО сотрудника",
    )
    position = models.CharField(
        max_length=100,
        verbose_name="Должность сотрудника",
        help_text="Укажите должность сотрудника",
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

        ordering = ("full_name",)

    def __str__(self):
        return f"{self.full_name} - {self.position}"


class Task(models.Model):
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("at_work", "В работе"),
        ("completed", "Выполнена"),
    ]

    title = models.CharField(
        max_length=100,
        verbose_name="Название задачи",
        help_text="Укажите название задачи",
    )
    parental_task = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subtasks",
        verbose_name="Родительская задача",
        help_text="Укажите родительскую задачу",
    )
    performer = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        verbose_name="Исполнитель",
        help_text="Укажите исполнителя",
    )
    deadline = models.DateTimeField(
        verbose_name="Срок",
        help_text="Укажите срок",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус",
        help_text="Укажите статус",
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

        ordering = ("-deadline",)

    def __str__(self):
        return f"{self.title} status: {self.status}"
