# Generated by Django 4.2.17 on 2025-04-11 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_remove_order_completed_at_alter_order_payment_method_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='shipping_address',
            new_name='address',
        ),
    ]
