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
        if highest is None:
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

        name = request.data.get('name', None)

        if name is None:
            name = "Kolumna " + str((Column.objects.order_by("-id").first().id+1) if Column.objects.exists() else 1)

        column_data = {
            'name': name,
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
            position = column.position
            columns_to_update = Column.objects.filter(position__gte=position)
            for col in columns_to_update:
                col.position -= 1
                col.save()
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

            name = request.data.get('name', '')

            if request.data['name'] == '':
                name = "Kolumna " + str(
                    (Column.objects.order_by("-id").first().id + 1) if Column.objects.exists() else 1)
            if 'max' in request.data:
                if request.data['max'] == None:
                    column.max = None
                elif request.data['max'] >= Note.objects.filter(column=column_id).count():
                    column.max = request.data['max']
                else:
                    column.max = Note.objects.filter(column=column_id).count()
            column.name = name
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
            notes = Note.objects.filter(column=column).order_by('position')

            serializer = NoteSerializer(notes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Column.DoesNotExist:
            return Response({"error": "Column does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        id = request.data['id']
        if not request.data['id']:
            return Response({"error": "Column does not exist"}, status=status.HTTP_404_NOT_FOUND)
        column = Column.objects.get(id=id)
        print(Note.objects.filter(id=id).count())
        print(column.max)
        if column.max is not None:
            if Note.objects.filter(column=id).count() >= column.max:
                return Response({"error": "Trying to add too many elements"}, status=status.HTTP_400_BAD_REQUEST)
        if column is None:
            return Response({"error": "Column does not exist"}, status=status.HTTP_404_NOT_FOUND)
        name = request.data.get('name', 'notatka ' + str((Note.objects.order_by("-id").first().id+1) if Note.objects.exists() else 1))
        position = 0
        if "position" in request.data is None:
            position = Note.objects.filter(column=id).order_by('-position').first().position + 1
        else:
            with transaction.atomic():
                notes_to_update = Note.objects.filter(column=column,position__gte=position)
                notes_to_update = notes_to_update.order_by('-position')
                for note in notes_to_update:
                    note.position += 1
                    note.save()
        note = Note.objects.create(name=name, column=column, position=position)
        note.save()
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def put(self, request):
        id = request.data.get('id', None)
        name = request.data.get('name', None)
        column = request.data.get('column', None)
        new_pos = request.data.get('position', None)

        if id is None:
            return Response({"error": "Note does not exist"}, status=status.HTTP_404_NOT_FOUND)

        note = Note.objects.get(id=request.data['id'])

        if note is None:
            return Response({"error": "Note does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if name is not None:
            note.name = request.data["name"]

        if column is not None:
            columnsMin = Column.objects.order_by("position").first().position-1
            print(Column.objects.filter(position=request.data['column']+columnsMin).exists())
            if Column.objects.filter(position=request.data['column']+columnsMin).exists():
                print(Column.objects.get(position=request.data['column']+columnsMin))
                note.column = Column.objects.get(position=request.data['column']+columnsMin)

            notes_to_update = Note.objects.filter(column=note.column, position__gte=note.position)
            notes_to_update.update(position=models.F('position') - 1)
            if new_pos is not None:
                notes_to_update = Note.objects.filter(column=column, position__gte=new_pos)
                notes_to_update.update(position=models.F('position') + 1)
            else:
                if Note.objects.filter(column=column).exists():
                    new_pos = Note.objects.filter(column=column).order_by("-position").first().position + 1
                else:
                    new_pos = 1
        elif new_pos is not None and new_pos != note.position:
            notes_to_update = Note.objects.filter(column=note.column,
                                                  position__gte=min(new_pos, note.position),
                                                  position__lte=max(new_pos, note.position)).exclude(
                id=note.id)
            if new_pos > note.position:
                notes_to_update.update(position=models.F('position') - 1)
            else:
                notes_to_update.update(position=models.F('position') + 1)
        else:
            if Note.objects.filter(column=note.column).exists():
                new_pos = Note.objects.filter(column=note.column).order_by("-position").first().position + 1
            else:
                new_pos = 1

        note.position = new_pos
        note.save()
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        if not request.data['id']:
            return Response({"error": "Note does not exist"}, status=status.HTTP_404_NOT_FOUND)
        note = Note.objects.get(id=request.data['id'])
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
