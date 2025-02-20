# Generated by Django 5.1.4 on 2024-12-14 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_bug_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_number', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to='app_versions/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
