# Generated by Django 2.1.7 on 2019-04-24 23:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('happyearth', '0007_auto_20190424_2316'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='dish',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='happyearth.Dish'),
        ),
        migrations.AddField(
            model_name='serve',
            name='dish',
            field=models.ForeignKey(default='a', on_delete=django.db.models.deletion.CASCADE, to='happyearth.Dish'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='serve',
            name='available',
        ),
        migrations.RemoveField(
            model_name='serve',
            name='price',
        ),
        migrations.RemoveField(
            model_name='serve',
            name='size',
        ),
        migrations.AlterUniqueTogether(
            name='serve',
            unique_together={('dish', 'restaurant')},
        ),
    ]
