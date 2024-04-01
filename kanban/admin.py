from django.contrib import admin

from .models import Column, Note, Person


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'max', 'per_person']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['name', 'column', 'position', 'person']

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name']
