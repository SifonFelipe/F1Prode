# Generated by Django 5.0.6 on 2024-06-26 02:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_alter_groupdetails_participants'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupdetails',
            name='participants',
            field=models.ManyToManyField(related_name='participants', to=settings.AUTH_USER_MODEL),
        ),
    ]
