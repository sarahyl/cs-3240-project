# Generated by Django 4.1.6 on 2023-04-13 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduleadvisor', '0002_student_advisor'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='comment',
            field=models.CharField(default='', max_length=1000),
        ),
    ]
