# Generated by Django 3.2.24 on 2024-02-28 00:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0093_auto_20240227_1753'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trade',
            name='exchange',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='leverage',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='mock',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='symbol',
        ),
        migrations.AlterField(
            model_name='trade',
            name='pipeline',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='model.pipeline'),
            preserve_default=False,
        ),
    ]
