# Generated by Django 4.0.5 on 2022-07-13 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rbdx', '0019_alter_usermodel_key_id_alter_usermodel_secret_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usermodel',
            name='key_id',
        ),
        migrations.RemoveField(
            model_name='usermodel',
            name='secret_key',
        ),
    ]
