# Generated by Django 2.1.7 on 2019-04-24 23:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('happyearth', '0005_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='dish',
        ),
        migrations.AlterUniqueTogether(
            name='serve',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='serve',
            name='dish',
        ),
    ]