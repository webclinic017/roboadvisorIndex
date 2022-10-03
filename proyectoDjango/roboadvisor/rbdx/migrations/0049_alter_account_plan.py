# Generated by Django 4.0.5 on 2022-09-22 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbdx', '0048_alter_account_plan_delete_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='plan',
            field=models.CharField(choices=[('F', 'Free'), ('P', 'Premium')], default='F', max_length=1),
        ),
    ]
