# Generated by Django 5.0.4 on 2024-04-22 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0008_accountholder_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountholder',
            name='set_password',
        ),
    ]
