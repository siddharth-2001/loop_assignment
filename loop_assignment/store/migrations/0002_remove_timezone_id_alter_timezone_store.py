# Generated by Django 4.2.5 on 2023-09-21 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timezone',
            name='id',
        ),
        migrations.AlterField(
            model_name='timezone',
            name='store',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='store.store'),
        ),
    ]