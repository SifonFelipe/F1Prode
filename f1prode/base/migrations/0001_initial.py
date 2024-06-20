# Generated by Django 5.0.4 on 2024-06-13 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('number', models.IntegerField()),
                ('team_name', models.CharField(max_length=60)),
                ('country', models.CharField(max_length=70)),
                ('headshot', models.URLField(max_length=500)),
            ],
        ),
    ]