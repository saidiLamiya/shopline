# Generated by Django 3.2.6 on 2022-01-07 21:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_product_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shippingaddress',
            old_name='Customer',
            new_name='customer',
        ),
    ]