# Generated by Django 4.0.5 on 2022-07-19 09:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbdx', '0025_indexshort_remove_index_is_active_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='index',
            old_name='IndexShort',
            new_name='indexShort',
        ),
        migrations.AlterField(
            model_name='stock',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 19, 11, 26, 22, 133119)),
        ),
    ]