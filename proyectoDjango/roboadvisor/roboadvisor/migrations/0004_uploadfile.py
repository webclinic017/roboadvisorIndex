# Generated by Django 4.0.5 on 2022-10-29 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roboadvisor', '0003_alter_order_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
            ],
        ),
    ]
