# Generated by Django 4.0.5 on 2022-10-03 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbdx', '0050_account_name_usermodel_is_premium_alter_account_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='index',
            name='account',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='rbdx.account'),
        ),
    ]
