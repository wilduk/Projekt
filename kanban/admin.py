from django.contrib import admin

from .models import Column


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'max']
