# Generated by Django 4.0 on 2024-11-19 08:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='image',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='like',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='share',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='usersession',
            options={'managed': False},
        ),
    ]
