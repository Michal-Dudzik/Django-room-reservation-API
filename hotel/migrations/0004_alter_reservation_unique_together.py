# Generated by Django 4.1.7 on 2023-02-28 01:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0003_alter_reservation_user_alter_room_description_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reservation',
            unique_together=set(),
        ),
    ]