# Generated by Django 2.1.7 on 2019-05-23 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app2', '0002_auto_20190522_1517'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='social',
            name='name',
        ),
    ]
