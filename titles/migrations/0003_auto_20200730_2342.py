# Generated by Django 3.0.5 on 2020-07-30 16:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0002_auto_20200730_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(1)]),
        ),
    ]
