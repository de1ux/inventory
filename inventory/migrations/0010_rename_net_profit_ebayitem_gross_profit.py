# Generated by Django 5.1 on 2024-09-05 03:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_ebayitem_net_profit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ebayitem',
            old_name='net_profit',
            new_name='gross_profit',
        ),
    ]
