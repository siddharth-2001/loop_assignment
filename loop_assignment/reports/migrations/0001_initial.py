# Generated by Django 4.2.5 on 2023-09-22 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('report_id', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=120)),
            ],
        ),
    ]