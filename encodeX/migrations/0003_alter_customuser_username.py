# Generated by Django 4.0.4 on 2024-01-01 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('encodeX', '0002_remove_customuser_credit_remove_customuser_groups_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=25),
        ),
    ]