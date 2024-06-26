# Generated by Django 5.0.4 on 2024-04-22 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0006_alter_account_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountHolder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=255)),
                ('set_password', models.CharField(max_length=50)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('currency', models.CharField(choices=[('E', 'Euro'), ('U', 'US Dollars'), ('G', 'British Pounds')], default='E', max_length=1)),
                ('balance', models.DecimalField(decimal_places=2, default=1000, max_digits=6)),
            ],
        ),
        migrations.DeleteModel(
            name='Account',
        ),
    ]
