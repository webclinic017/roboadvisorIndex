# Generated by Django 4.0.5 on 2022-07-05 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbdx', '0008_user_keyid_user_secretkey'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='rbdx.user'),
        ),
    ]