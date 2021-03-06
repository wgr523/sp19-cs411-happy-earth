# Generated by Django 2.1.7 on 2019-04-16 02:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('happyearth', '0003_auto_20190404_0209'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recommend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='happyearth.Restaurant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='happyearth.User')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='recommend',
            unique_together={('user', 'restaurant')},
        ),
    ]
