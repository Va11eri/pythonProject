# Generated by Django 4.2.3 on 2023-07-29 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='response',
            options={'ordering': ['-sent_at']},
        ),
    ]
