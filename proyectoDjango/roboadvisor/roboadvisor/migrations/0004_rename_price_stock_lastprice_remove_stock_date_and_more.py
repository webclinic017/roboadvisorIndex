# Generated by Django 4.0.5 on 2022-10-22 11:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('roboadvisor', '0003_remove_index_equity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stock',
            old_name='price',
            new_name='lastPrice',
        ),
        migrations.RemoveField(
            model_name='stock',
            name='date',
        ),
        migrations.AddField(
            model_name='order',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]
