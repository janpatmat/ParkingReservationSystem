# Generated by Django 5.2.3 on 2025-06-16 06:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_remove_parkingspot_occupied'),
    ]

    operations = [
        migrations.CreateModel(
            name='Archive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(blank=True, max_length=255, null=True)),
                ('date_in', models.DateTimeField()),
                ('date_out', models.DateTimeField()),
                ('status', models.CharField(max_length=50)),
                ('spotID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.parkingspot')),
            ],
            options={
                'db_table': 'archive',
            },
        ),
    ]
