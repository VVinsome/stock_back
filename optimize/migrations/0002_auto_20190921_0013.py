# Generated by Django 2.2.5 on 2019-09-21 00:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('optimize', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='price',
            options={'ordering': ['-date']},
        ),
    ]
