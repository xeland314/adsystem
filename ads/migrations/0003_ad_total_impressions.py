# Generated by Django 5.2.2 on 2025-06-26 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0002_ad_display_days_of_week_ad_display_end_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='total_impressions',
            field=models.PositiveIntegerField(default=0, verbose_name='Total de Impresiones'),
        ),
    ]
