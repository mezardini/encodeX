# Generated by Django 4.0.4 on 2024-01-11 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('encodeX', '0008_alter_encodedimage_date_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='encodedimage',
            name='message_id',
            field=models.IntegerField(null=True, unique=True),
        ),
    ]
