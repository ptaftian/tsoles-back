# Generated by Django 5.1.4 on 2024-12-14 09:54

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_user_username_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='bug',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
