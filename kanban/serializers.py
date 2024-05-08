from rest_framework import serializers
from .models import Column, Note, Team


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
