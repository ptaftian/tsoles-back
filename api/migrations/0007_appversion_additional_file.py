# Generated by Django 5.1.4 on 2024-12-17 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_user_phone_number_user_serial_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='appversion',
            name='additional_file',
            field=models.FileField(blank=True, null=True, upload_to='app_versions/'),
        ),
    ]
