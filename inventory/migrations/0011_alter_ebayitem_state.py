# Generated by Django 5.1 on 2024-09-05 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_rename_net_profit_ebayitem_gross_profit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebayitem',
            name='state',
            field=models.CharField(choices=[('IN_FLIGHT', 'in flight'), ('ON_SHELF', 'on shelf'), ('ON_SHELF_LISTED', 'listed'), ('SHIPPED', 'shipped')], default='IN_FLIGHT', max_length=255),
        ),
    ]
