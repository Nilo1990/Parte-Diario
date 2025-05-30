# Generated by Django 5.1.6 on 2025-05-20 13:20

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ParteDiario', '0003_remove_registroservicio_parte_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='partediario',
            options={'ordering': ['-fecha']},
        ),
        migrations.AlterField(
            model_name='servicioregistro',
            name='fecha_registro',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Fecha de registro'),
        ),
        migrations.AlterUniqueTogether(
            name='partediario',
            unique_together={('fecha', 'municipio')},
        ),
        migrations.DeleteModel(
            name='LogCambios',
        ),
    ]
