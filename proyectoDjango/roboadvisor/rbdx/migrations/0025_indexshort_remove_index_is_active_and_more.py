# Generated by Django 4.0.5 on 2022-07-18 15:25

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbdx', '0024_index_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndexShort',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(default=None, max_length=5)),
            ],
        ),
        migrations.RemoveField(
            model_name='index',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='index',
            name='symbol',
        ),
        migrations.AlterField(
            model_name='index',
            name='equity',
            field=models.FloatField(default=10000),
        ),
        migrations.AlterField(
            model_name='index',
            name='marketCap',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='stock',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 18, 17, 25, 54, 636045)),
        ),
        migrations.AddField(
            model_name='index',
            name='IndexShort',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='rbdx.indexshort'),
        ),
    ]