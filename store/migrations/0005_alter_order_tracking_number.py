# Generated by Django 4.2 on 2025-04-05 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_alter_order_id_alter_order_tracking_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="tracking_number",
            field=models.UUIDField(default="A94BF6447098412F8F5E", editable=False),
        ),
    ]
