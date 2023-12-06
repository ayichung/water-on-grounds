# Generated by Django 4.2.5 on 2023-10-22 20:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import water.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('place_id', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='WaterStation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('floor', models.IntegerField(default=1)),
                ('cardinal', models.CharField(max_length=1)),
                ('traditional', models.BooleanField()),
                ('bottle', models.BooleanField()),
                ('approved', models.BooleanField()),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='water.building')),
                ('user', models.ForeignKey(on_delete=models.SET(water.models.get_null_user), to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
