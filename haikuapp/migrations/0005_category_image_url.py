# Generated by Django 2.0.6 on 2018-08-03 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haikuapp', '0004_auto_20180803_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image_url',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]