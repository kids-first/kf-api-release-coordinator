# Generated by Django 2.1.11 on 2019-10-20 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20190815_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='message',
            field=models.CharField(help_text='The message describing the event', max_length=1000),
        ),
    ]
