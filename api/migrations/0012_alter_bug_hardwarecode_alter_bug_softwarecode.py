# Generated by Django 5.1.4 on 2024-12-18 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_examination'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bug',
            name='hardwareCode',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='bug',
            name='softwareCode',
            field=models.CharField(max_length=100),
        ),
    ]
