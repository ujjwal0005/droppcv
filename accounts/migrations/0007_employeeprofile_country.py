# Generated by Django 5.1.5 on 2025-02-05 12:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_employeeprofile_service_type_alter_user_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeprofile',
            name='country',
            field=models.CharField(default=datetime.time, max_length=255),
            preserve_default=False,
        ),
    ]
