# Generated by Django 5.2.2 on 2025-06-09 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datacollectors_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('deployed', 'Deployed')], default='available', max_length=20),
        ),
    ]
