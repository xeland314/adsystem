# Generated by Django 5.2.2 on 2025-06-26 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0004_conversion'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='ab_test_group',
            field=models.CharField(blank=True, help_text="Identificador del grupo de prueba A/B al que pertenece este anuncio (ej. 'Control', 'Variante A').", max_length=50, verbose_name='Grupo de Prueba A/B'),
        ),
    ]
