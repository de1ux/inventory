# Generated by Django 5.1 on 2024-09-03 01:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_ebayitem_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitem',
            name='bought_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 3, 1, 46, 0, 155825, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]
