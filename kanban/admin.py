from django.contrib import admin

from .models import Column, Note


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'max']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['name', 'column']
