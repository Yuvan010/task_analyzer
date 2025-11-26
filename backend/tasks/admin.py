from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "due_date", "estimated_hours", "importance")
    list_filter = ("due_date", "importance")
    search_fields = ("title",)
