# Generated by Django 5.2.3 on 2025-06-15 20:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_parkingspot_occupied_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parkingspot',
            name='reserveStatus',
        ),
    ]
