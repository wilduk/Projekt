# Generated by Django 5.0.3 on 2024-03-31 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0006_person_note_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='per_person',
            field=models.BooleanField(default=False),
        ),
    ]