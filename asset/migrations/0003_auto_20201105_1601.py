# Generated by Django 2.2.4 on 2020-11-05 16:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0002_auto_20201101_1507'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='type_name',
        ),
        migrations.RemoveField(
            model_name='historicalasset',
            name='type_name',
        ),
    ]
