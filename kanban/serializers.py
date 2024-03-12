from rest_framework import serializers
from .models import Column, Object


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = '__all__'


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = '__all__'
