# Generated by Django 5.2.3 on 2025-07-04 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('vehicle_type', models.CharField(max_length=50, verbose_name='Vehicle Type')),
                ('icon', models.ImageField(upload_to='vehicle_icons/', verbose_name='Icon')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
