# Generated by Django 5.1 on 2024-09-01 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ebay_refresh_token',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='ebay_token',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
