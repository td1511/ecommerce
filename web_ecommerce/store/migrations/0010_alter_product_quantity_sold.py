# Generated by Django 4.2.17 on 2025-04-07 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_rename_created_by_id_product_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='quantity_sold',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
