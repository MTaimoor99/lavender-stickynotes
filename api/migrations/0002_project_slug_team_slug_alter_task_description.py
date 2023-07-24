# Generated by Django 4.2.3 on 2023-07-24 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='slug',
            field=models.SlugField(default='sugdiuadga6f', max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='slug',
            field=models.SlugField(default='bfewiugefyify', max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.CharField(max_length=500),
        ),
    ]