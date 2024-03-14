from django.shortcuts import render
from django.views import View
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Column, Note
from django.views.generic.edit import CreateView
from django.db import transaction
from .serializers import ColumnSerializer, NoteSerializer


class ColumnAPIView(APIView):
    def post(self, request):
        position = request.data.get('position')
        highest = Column.objects.order_by('-position').first()

        if position is None:
            if highest:
                position = highest.position + 1
            else:
                position = 1
        elif position > highest.position:
            position = highest.position + 1
        else:
            with transaction.atomic():
                columns_to_update = Column.objects.filter(position__gte=position)
                columns_to_update = columns_to_update.order_by('-position')
                for column in columns_to_update:
                    column.position += 1
                    column.save()

        column_data = {
            'name': request.data.get('name', ''),
            'position': position,
            'max': request.data.get('max', None)
        }

        print(column_data)

        serializer = ColumnSerializer(data=column_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        columns = Column.objects.all().order_by('position')
        serializer = ColumnSerializer(columns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            column_id = request.data['id']
            column = Column.objects.get(id=column_id)
            column.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Column.DoesNotExist:
            return Response({"error": "Column does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            column_id = request.data['id']
            new_position = request.data.get('position')
            column = Column.objects.get(id=column_id)
            if new_position is not None and new_position != column.position:
                columns_to_update = Column.objects.filter(position__gte=min(new_position, column.position),
                                                          position__lte=max(new_position, column.position)).exclude(
                    id=column_id)
                if new_position > column.position:
                    columns_to_update.update(position=models.F('position') - 1)
                else:
                    columns_to_update.update(position=models.F('position') + 1)

                column.position = new_position

            if 'name' in request.data:
                column.name = request.data['name']
            if 'max' in request.data:
                column.max = request.data['max']
            column.save()
            return Response(ColumnSerializer(column).data, status=status.HTTP_200_OK)
        except Column.DoesNotExist:
            return Response({"error": "Column does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ColumnHTMLView(View):
    def get(self, request):
        api_view_instance = ColumnAPIView()
        api_response = api_view_instance.get(request)
        data = api_response.data

        return render(request, 'your_template.html', {'data': data}) # to już wam zostawiam

    def post(self, request):
        api_view_instance = ColumnAPIView()
        api_response = api_view_instance.post(request)
        data = api_response.data

        return render(request, 'your_template.html', {'data': data})  # to już wam zostawiam

    def put(self, request):
        api_view_instance = ColumnAPIView()
        api_response = api_view_instance.put(request)
        data = api_response.data

        return render(request, 'your_template.html', {'data': data})  # to już wam zostawiam

    def delete(self, request):
        api_view_instance = ColumnAPIView()
        api_response = api_view_instance.delete(request)
        data = api_response.data

        return render(request, 'your_template.html', {'data': data})  # to już wam zostawiam


class NoteAPIView(APIView):
    def get(self, request):
        try:
            id = request.GET.get('id')
            column = Column.objects.get(id=id)
            notes = Note.objects.filter(column=column)

            serializer = NoteSerializer(notes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Column.DoesNotExist:
            return Response({"error": "Column does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if not request.data['id']:
            return Response({"error": "Column does not exist"}, status=status.HTTP_404_NOT_FOUND)
        column = Column.objects.get(id=id)
        if column is None:
            return Response({"error": "Column does not exist"}, status=status.HTTP_404_NOT_FOUND)
        name = request.data['name'] or ""
        note = Note.objects.create(name=name, column=column)
        note.save()
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def put(self, request):
        if not request.data['id']:
            return Response({"error": "Note does not exist"}, status=status.HTTP_404_NOT_FOUND)
        note = Note.objects.get(id=id)
        if note is None:
            return Response({"error": "Note does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if request.data['name']:
            note.name = request.data["name"]
        note.save()
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        if not request.data['id']:
            return Response({"error": "Note does not exist"}, status=status.HTTP_404_NOT_FOUND)
        note = Note.objects.get(id=id)
        if note is None:
            return Response({"error": "Note does not exist"}, status=status.HTTP_404_NOT_FOUND)
        note.delete()
        return Response(status=status.HTTP_200_OK)


class NoteHTMLView(View):
    def get(self, request):
        api_view_instance = NoteAPIView()
        api_response = api_view_instance.get(request)
        data = api_response.data

        return render(request, 'your_template.html', {'data': data}) # to już wam zostawiam

    def post(self, request):
        api_view_instance = NoteAPIView()
        api_response = api_view_instance.post(request)
        data = api_response.data

        return render(request, 'your_template.html', {'data': data})  # to już wam zostawiam

    def put(self, request):
        api_view_instance = NoteAPIView()
        api_response = api_view_instance.put(request)
        data = api_response.data

        return render(request, 'your_template.html', {'data': data})  # to już wam zostawiam

    def delete(self, request):
        api_view_instance = NoteAPIView()
        api_response = api_view_instance.delete(request)
        data = api_response.data

        return render(request, 'your_template.html', {'data': data})  # to już wam zostawiam
