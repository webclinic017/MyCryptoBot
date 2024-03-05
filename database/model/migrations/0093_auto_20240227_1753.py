# Generated by Django 3.2.24 on 2024-02-27 23:53

from django.db import migrations, models
import django.db.models.deletion


def delete_referecing_null(apps, _):
    Position = apps.get_model('model', 'Position')

    Position.objects.filter(pipeline__id=None).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0092_run_trade_pnl'),
    ]

    operations = [
        migrations.RunPython(delete_referecing_null),
        migrations.RemoveField(
            model_name='position',
            name='exchange',
        ),
        migrations.RemoveField(
            model_name='position',
            name='open',
        ),
        migrations.RemoveField(
            model_name='position',
            name='paper_trading',
        ),
        migrations.RemoveField(
            model_name='position',
            name='symbol',
        ),
        migrations.AlterField(
            model_name='position',
            name='pipeline',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='model.pipeline'),
            preserve_default=False,
        ),
    ]