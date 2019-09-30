# Generated by Django 2.2.5 on 2019-09-20 23:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('close_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('date', models.DateField()),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='optimize.Stock')),
            ],
        ),
    ]
